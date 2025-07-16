from datetime import datetime, timezone
import json
import os
from functools import wraps

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# 数据库连接配置 - 使用正确的root用户名
DATABASE_URL = "postgresql://root:Bjtu2025@122.9.0.229:5432/bjtu"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

taxi_data_router = APIRouter()

from pathlib import Path


def api_exception_handler(error_message):
    """API异常处理装饰器
    
    Args:
        error_message: 错误消息前缀
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"{error_message}: {str(e)}")
        return wrapper
    return decorator



class HeatmapPoint(BaseModel):
    lng: float
    lat: float
    count: int

class ClusterInfo(BaseModel):
    center_latitude: float
    center_longitude: float
    count: int
    avg_distance_km: float
    avg_duration_minutes: float

class TimeStats(BaseModel):
    hour: int
    vehicle_count: int
    avg_distance: float
    avg_duration: float

# 添加通用的网格聚合处理函数
def aggregate_grid_data(result, grid_size, count_field_index=None):
    """通用网格聚合处理函数
    
    Args:
        result: 数据库查询结果
        grid_size: 网格大小
        count_field_index: 计数字段索引，如果提供则使用该字段值作为计数，否则默认为1
    
    Returns:
        网格聚合后的字典 {(lat, lng): count}
    """
    grid_dict = {}
    for row in result:
        try:
            lat = float(row[0])
            lng = float(row[1])
            count = int(row[count_field_index]) if count_field_index is not None else 1
            
            # 网格聚合
            grid_lat = round(lat / grid_size) * grid_size
            grid_lng = round(lng / grid_size) * grid_size
            grid_key = (grid_lat, grid_lng)
            
            grid_dict[grid_key] = grid_dict.get(grid_key, 0) + count
            
        except (ValueError, KeyError, IndexError) as e:
            # 跳过无效数据
            continue
    
    return grid_dict

def convert_to_heatmap_points(grid_dict, max_points):
    """将网格字典转换为热力图点列表
    
    Args:
        grid_dict: 网格聚合后的字典 {(lat, lng): count}
        max_points: 最大返回点数
    
    Returns:
        热力图点列表
    """
    # 转换为热力图点
    heatmap_points = []
    for (lat, lng), count in grid_dict.items():
        point = HeatmapPoint(
            lng=float(lng),
            lat=float(lat),
            count=count
        )
        heatmap_points.append(point)
    
    # 按权重排序并限制数量
    heatmap_points.sort(key=lambda x: x.count, reverse=True)
    return heatmap_points[:max_points]

# UTC时间范围热力图API性能优化
@taxi_data_router.get("/taxi/heatmap-data-utc", response_model=List[HeatmapPoint])
@api_exception_handler("处理UTC时间范围数据失败")
async def get_heatmap_data_utc(
    start_utc: Optional[str] = Query(None, description="起始UTC时间 (格式: YYYY-MM-DD HH:MM:SS)"),
    end_utc: Optional[str] = Query(None, description="结束UTC时间 (格式: YYYY-MM-DD HH:MM:SS)"),
    max_points: Optional[int] = Query(8000, description="最大返回点数"),
    grid_size: Optional[float] = Query(0.005, description="网格聚合大小(度)"),
    db: Session = Depends(get_db)
):
    """获取热力图数据 - 基于UTC时间范围过滤，性能优化版本"""
    # 构建SQL查询
    query = """
    SELECT latitude_bd09, longitude_bd09
    FROM cleaned_taxi_trajectory
    WHERE 1=1
    """
    
    params = {}
    
    # 如果指定了时间范围，进行过滤
    if start_utc and end_utc:
        # 将UTC时间转换为本地时间（数据库中存储的是本地时间）
        start_time = pd.to_datetime(start_utc) + pd.Timedelta(hours=8)
        end_time = pd.to_datetime(end_utc) + pd.Timedelta(hours=8)
        
        query += " AND timestamp >= :start_time AND timestamp <= :end_time"
        params['start_time'] = start_time.strftime('%Y/%m/%d %H:%M:%S')
        params['end_time'] = end_time.strftime('%Y/%m/%d %H:%M:%S')
    
    # 限制查询数量并添加随机采样
    query += " AND random() < 0.1 LIMIT 500000"
    
    # 执行查询
    result = db.execute(text(query), params)
    
    # 使用通用函数处理数据
    grid_dict = aggregate_grid_data(result, grid_size)
    return convert_to_heatmap_points(grid_dict, max_points)

# 新增：获取UTC时间范围统计信息
@taxi_data_router.get("/taxi/utc-time-stats")
async def get_utc_time_stats(
    start_utc: str = Query(..., description="起始UTC时间 (格式: YYYY-MM-DD HH:MM:SS)"),
    end_utc: str = Query(..., description="结束UTC时间 (格式: YYYY-MM-DD HH:MM:SS)"),
    db: Session = Depends(get_db)
):
    """获取指定UTC时间范围的统计信息"""
    try:
        # 将UTC时间转换为本地时间
        start_local = pd.to_datetime(start_utc) + pd.Timedelta(hours=8)
        end_local = pd.to_datetime(end_utc) + pd.Timedelta(hours=8)
        
        # 查询OD数据统计
        query = """
        SELECT 
            COUNT(*) as total_trips,
            COUNT(DISTINCT vehicle_id) as unique_vehicles,
            AVG(CASE 
                WHEN pick_up_latitude IS NOT NULL AND pick_up_longitude IS NOT NULL 
                     AND drop_off_latitude IS NOT NULL AND drop_off_longitude IS NOT NULL
                THEN 6371 * acos(cos(radians(pick_up_latitude)) * cos(radians(drop_off_latitude)) 
                     * cos(radians(drop_off_longitude) - radians(pick_up_longitude)) 
                     + sin(radians(pick_up_latitude)) * sin(radians(drop_off_latitude)))
                ELSE NULL
            END) as avg_distance
        FROM taxi_od_clusters
        WHERE pick_up_timestamp >= :start_time AND pick_up_timestamp <= :end_time
        LIMIT 50000
        """
        
        result = db.execute(text(query), {
            'start_time': start_local.strftime('%Y/%m/%d %H:%M'),
            'end_time': end_local.strftime('%Y/%m/%d %H:%M')
        })
        
        row = result.fetchone()
        
        return {
            "time_range": f"{start_utc} - {end_utc} (UTC)",
            "total_trips": row[0] if row[0] else 0,
            "unique_vehicles": row[1] if row[1] else 0,
            "avg_distance": round(row[2], 2) if row[2] else 0,
            "avg_duration": 0  # 需要根据实际数据计算
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取UTC时间统计失败: {str(e)}")

@taxi_data_router.get("/taxi/od-data")
async def get_od_data(
    limit: Optional[int] = 1000,
    db: Session = Depends(get_db)
):
    """获取OD数据 - 用于轨迹可视化"""
    try:
        query = """
        SELECT vehicle_id, pick_up_timestamp, pick_up_latitude, pick_up_longitude,
               drop_off_timestamp, drop_off_latitude, drop_off_longitude, pick_up_cluster
        FROM taxi_od_clusters
        WHERE pick_up_latitude IS NOT NULL AND pick_up_longitude IS NOT NULL
              AND drop_off_latitude IS NOT NULL AND drop_off_longitude IS NOT NULL
        ORDER BY pick_up_timestamp
        LIMIT :limit
        """
        
        result = db.execute(text(query), {'limit': limit})
        rows = result.fetchall()
        
        od_data = []
        for row in rows:
            od_data.append({
                'vehicle_id': row[0],
                'pick_up_timestamp': row[1],
                'pick_up_latitude': row[2],
                'pick_up_longitude': row[3],
                'drop_off_timestamp': row[4],
                'drop_off_latitude': row[5],
                'drop_off_longitude': row[6],
                'pick_up_cluster': row[7]
            })
        
        return od_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取OD数据失败: {str(e)}")

@taxi_data_router.get("/taxi/trajectory-data")
async def get_trajectory_data(
    vehicle_id: Optional[str] = None, 
    limit: Optional[int] = 5000,
    db: Session = Depends(get_db)
):
    """获取轨迹数据"""
    try:
        query = """
        SELECT vehicle_id, timestamp, latitude_bd09, longitude_bd09, 
               heading, speed, occupied
        FROM cleaned_taxi_trajectory
        WHERE latitude_bd09 IS NOT NULL AND longitude_bd09 IS NOT NULL
        """
        
        params = {'limit': limit}
        
        # 如果指定了车辆ID，则过滤
        if vehicle_id:
            query += " AND vehicle_id = :vehicle_id"
            params['vehicle_id'] = vehicle_id
        
        query += " ORDER BY timestamp LIMIT :limit"
        
        result = db.execute(text(query), params)
        rows = result.fetchall()
        
        trajectory_data = []
        for row in rows:
            trajectory_data.append({
                'vehicle_id': row[0],
                'timestamp': row[1],
                'latitude_bd09': row[2],
                'longitude_bd09': row[3],
                'heading': row[4],
                'speed': row[5],
                'occupied': row[6]
            })
        
        return trajectory_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取轨迹数据失败: {str(e)}")

@taxi_data_router.get("/taxi/vehicle-track")
async def get_vehicle_track(
    vehicle_id: str,
    start_time: str,  # 改为直接接收北京时间
    end_time: str,    # 改为直接接收北京时间
    db: Session = Depends(get_db)
):
    """获取指定车辆在指定时间范围内的轨迹数据"""
    try:
        # 打印接收到的原始参数
        print(f"接收到的参数 - 车辆ID: {vehicle_id}, 开始时间: {start_time}, 结束时间: {end_time}")
        
        # 不再转换时间格式，直接使用前端传来的格式（带连字符的格式）
        # start_time_formatted = start_time.replace('-', '/')
        # end_time_formatted = end_time.replace('-', '/')
        start_time_formatted = start_time
        end_time_formatted = end_time
        
        # 打印使用的时间格式
        print(f"使用的时间格式 - 开始时间: {start_time_formatted}, 结束时间: {end_time_formatted}")
        
        # 先执行一个测试查询，检查是否有该车辆的数据
        test_query = """
        SELECT COUNT(*) 
        FROM cleaned_taxi_trajectory 
        WHERE vehicle_id = :vehicle_id
        """
        
        test_result = db.execute(text(test_query), {'vehicle_id': vehicle_id})
        vehicle_count = test_result.scalar()
        print(f"数据库中车辆 {vehicle_id} 的记录数: {vehicle_count}")
        
        # 再执行一个测试查询，检查时间范围内是否有数据
        time_test_query = """
        SELECT MIN(timestamp), MAX(timestamp) 
        FROM cleaned_taxi_trajectory 
        WHERE vehicle_id = :vehicle_id
        """
        
        time_test_result = db.execute(text(time_test_query), {'vehicle_id': vehicle_id})
        time_range = time_test_result.fetchone()
        if time_range and time_range[0] and time_range[1]:
            print(f"车辆 {vehicle_id} 的时间范围: {time_range[0]} 到 {time_range[1]}")
        else:
            print(f"未找到车辆 {vehicle_id} 的时间范围信息")
        
        # 使用原始时间格式查询
        query = """
        SELECT longitude_bd09, latitude_bd09, timestamp, occupied
        FROM cleaned_taxi_trajectory
        WHERE vehicle_id = :vehicle_id
              AND timestamp >= :start_time AND timestamp <= :end_time
              AND latitude_bd09 IS NOT NULL AND longitude_bd09 IS NOT NULL
        ORDER BY timestamp
        LIMIT 10000
        """
        
        result = db.execute(text(query), {
            'vehicle_id': vehicle_id,
            'start_time': start_time_formatted,  # 使用原始时间格式
            'end_time': end_time_formatted
        })
        
        rows = result.fetchall()
        print(f"查询结果行数: {len(rows)}")
        
        vehicle_tracks = []
        
        for row in rows:
            vehicle_tracks.append({
                "lng": float(row[0]),
                "lat": float(row[1]),
                "timestamp": row[2],  # 直接返回数据库中的时间戳
                "status": int(row[3]) if row[3] else 0
            })
        
        return vehicle_tracks
        
    except Exception as e:
        print(f"获取车辆轨迹数据时出错: {e}")
        return []

@taxi_data_router.get("/taxi/heatmap-data", response_model=List[HeatmapPoint])
async def get_heatmap_data(
    start_hour: Optional[int] = Query(None, ge=0, le=23, description="起始小时 (0-23)"),
    end_hour: Optional[int] = Query(None, ge=0, le=23, description="结束小时 (0-23)"),
    db: Session = Depends(get_db)
):
    """获取热力图数据 - 基于聚类中心，支持时间过滤"""
    try:
        # 构建时间过滤条件
        time_filter = ""
        params = {}
        
        if start_hour is not None and end_hour is not None:
            if start_hour <= end_hour:
                time_filter = "AND EXTRACT(HOUR FROM TO_TIMESTAMP(pick_up_timestamp, 'YYYY/MM/DD HH24:MI')) BETWEEN :start_hour AND :end_hour"
            else:  # 跨天情况
                time_filter = "AND (EXTRACT(HOUR FROM TO_TIMESTAMP(pick_up_timestamp, 'YYYY/MM/DD HH24:MI')) >= :start_hour OR EXTRACT(HOUR FROM TO_TIMESTAMP(pick_up_timestamp, 'YYYY/MM/DD HH24:MI')) <= :end_hour)"
            
            params['start_hour'] = start_hour
            params['end_hour'] = end_hour
        
        # 基于聚类中心生成热力图
        query = f"""
        SELECT pick_up_cluster, 
               AVG(pick_up_latitude) as center_lat,
               AVG(pick_up_longitude) as center_lng,
               COUNT(*) as count
        FROM taxi_od_clusters
        WHERE pick_up_cluster != -1 
              AND pick_up_latitude IS NOT NULL 
              AND pick_up_longitude IS NOT NULL
              {time_filter}
        GROUP BY pick_up_cluster
        HAVING COUNT(*) > 5
        ORDER BY count DESC
        LIMIT 5000
        """
        
        result = db.execute(text(query), params)
        rows = result.fetchall()
        
        heatmap_points = []
        for row in rows:
            point = HeatmapPoint(
                lng=float(row[2]),
                lat=float(row[1]),
                count=int(row[3])
            )
            heatmap_points.append(point)
        
        return heatmap_points
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取聚类数据失败: {str(e)}")

@taxi_data_router.get("/taxi/time-range-stats")
async def get_time_range_stats(
    start_hour: int = Query(..., ge=0, le=23, description="起始小时 (0-23)"),
    end_hour: int = Query(..., ge=0, le=23, description="结束小时 (0-23)"),
    db: Session = Depends(get_db)
):
    """获取指定时间范围的统计信息"""
    try:
        # 构建时间过滤条件
        if start_hour <= end_hour:
            time_filter = "AND EXTRACT(HOUR FROM TO_TIMESTAMP(pick_up_timestamp, 'YYYY/MM/DD HH24:MI')) BETWEEN :start_hour AND :end_hour"
        else:  # 跨天情况
            time_filter = "AND (EXTRACT(HOUR FROM TO_TIMESTAMP(pick_up_timestamp, 'YYYY/MM/DD HH24:MI')) >= :start_hour OR EXTRACT(HOUR FROM TO_TIMESTAMP(pick_up_timestamp, 'YYYY/MM/DD HH24:MI')) <= :end_hour)"
        
        query = f"""
        SELECT 
            COUNT(DISTINCT vehicle_id) as total_vehicles,
            AVG(CASE 
                WHEN pick_up_latitude IS NOT NULL AND pick_up_longitude IS NOT NULL 
                     AND drop_off_latitude IS NOT NULL AND drop_off_longitude IS NOT NULL
                THEN 6371 * acos(cos(radians(pick_up_latitude)) * cos(radians(drop_off_latitude)) 
                     * cos(radians(drop_off_longitude) - radians(pick_up_longitude)) 
                     + sin(radians(pick_up_latitude)) * sin(radians(drop_off_latitude)))
                ELSE NULL
            END) as avg_distance
        FROM taxi_od_clusters
        WHERE 1=1 {time_filter}
        LIMIT 50000
        """
        
        result = db.execute(text(query), {
            'start_hour': start_hour,
            'end_hour': end_hour
        })
        
        row = result.fetchone()
        
        # 处理跨天的时间范围
        if start_hour <= end_hour:
            hours = list(range(start_hour, end_hour + 1))
        else:  # 跨天情况
            hours = list(range(start_hour, 24)) + list(range(0, end_hour + 1))
        
        return {
            "time_range": f"{start_hour:02d}:00 - {end_hour:02d}:59",
            "total_vehicles": row[0] if row[0] else 0,
            "avg_distance": round(row[1], 2) if row[1] else 0,
            "avg_duration": 0,  # 需要根据实际数据计算
            "hours_included": hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取时间统计数据失败: {str(e)}")

@taxi_data_router.get("/taxi/data-distribution")
async def get_data_distribution(db: Session = Depends(get_db)):
    """获取数据地理分布统计"""
    try:
        query = """
        SELECT 
            MIN(latitude_bd09) as lat_min,
            MAX(latitude_bd09) as lat_max,
            MIN(longitude_bd09) as lng_min,
            MAX(longitude_bd09) as lng_max,
            AVG(latitude_bd09) as lat_avg
        FROM cleaned_taxi_trajectory
        WHERE latitude_bd09 IS NOT NULL AND longitude_bd09 IS NOT NULL
        LIMIT 100000
        """
        
        result = db.execute(text(query))
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="没有找到轨迹数据")
        
        lat_min, lat_max, lng_min, lng_max, lat_avg = row
        
        # 按纬度分区统计
        count_query = """
        SELECT 
            SUM(CASE WHEN latitude_bd09 > :lat_avg THEN 1 ELSE 0 END) as north_count,
            SUM(CASE WHEN latitude_bd09 <= :lat_avg THEN 1 ELSE 0 END) as south_count,
            COUNT(*) as total_count
        FROM cleaned_taxi_trajectory
        WHERE latitude_bd09 IS NOT NULL AND longitude_bd09 IS NOT NULL
        LIMIT 100000
        """
        
        count_result = db.execute(text(count_query), {'lat_avg': lat_avg})
        count_row = count_result.fetchone()
        
        north_count, south_count, total_count = count_row
        
        return {
            "coordinate_range": {
                "lat_min": lat_min,
                "lat_max": lat_max,
                "lng_min": lng_min,
                "lng_max": lng_max
            },
            "distribution": {
                "north_count": north_count,
                "south_count": south_count,
                "north_percentage": round(north_count / total_count * 100, 2) if total_count > 0 else 0,
                "south_percentage": round(south_count / total_count * 100, 2) if total_count > 0 else 0
            },
            "total_points": total_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据分布失败: {str(e)}")

@taxi_data_router.get("/taxi/heatmap-data-fast", response_model=List[HeatmapPoint])
async def get_heatmap_data_fast(
    max_points: Optional[int] = Query(5000, description="最大返回点数"),
    db: Session = Depends(get_db)
):
    """快速热力图数据 - 使用预处理的聚类数据"""
    try:
        query = """
        SELECT pick_up_cluster,
               AVG(pick_up_latitude) as center_lat,
               AVG(pick_up_longitude) as center_lng,
               COUNT(*) as count
        FROM taxi_od_clusters
        WHERE pick_up_cluster != -1 
              AND pick_up_latitude IS NOT NULL 
              AND pick_up_longitude IS NOT NULL
        GROUP BY pick_up_cluster
        HAVING COUNT(*) > 3
        ORDER BY count DESC
        LIMIT :max_points
        """
        
        result = db.execute(text(query), {'max_points': max_points})
        rows = result.fetchall()
        
        heatmap_points = []
        for row in rows:
            point = HeatmapPoint(
                lng=float(row[2]),
                lat=float(row[1]),
                count=int(row[3])
            )
            heatmap_points.append(point)
        
        return heatmap_points
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取快速热力图数据失败: {str(e)}")

@taxi_data_router.get("/taxi/trajectory-heatmap-data", response_model=List[HeatmapPoint])
async def get_trajectory_heatmap_data(
    sample_rate: Optional[float] = Query(0.03, description="采样率 (0.01-1.0)"),
    grid_size: Optional[float] = Query(0.005, description="网格大小 (度)"),
    max_points: Optional[int] = Query(6000, description="最大返回点数"),
    db: Session = Depends(get_db)
):
    """获取基于原始轨迹数据的热力图数据 - 性能优化版本"""
    try:
        # 使用随机采样来减少数据量
        query = """
        SELECT latitude_bd09, longitude_bd09
        FROM cleaned_taxi_trajectory
        WHERE latitude_bd09 IS NOT NULL AND longitude_bd09 IS NOT NULL
              AND random() < :sample_rate
        LIMIT 50000
        """
        
        result = db.execute(text(query), {'sample_rate': sample_rate})
        rows = result.fetchall()
        
        # 网格聚合
        grid_dict = {}
        for row in rows:
            lat, lng = row[0], row[1]
            grid_lat = round(lat / grid_size) * grid_size
            grid_lng = round(lng / grid_size) * grid_size
            grid_key = (grid_lat, grid_lng)
            
            if grid_key in grid_dict:
                grid_dict[grid_key] += 1
            else:
                grid_dict[grid_key] = 1
        
        # 转换为热力图点
        heatmap_points = []
        for (lat, lng), count in grid_dict.items():
            point = HeatmapPoint(
                lng=float(lng),
                lat=float(lat),
                count=count
            )
            heatmap_points.append(point)
        
        # 按权重排序并限制返回数量
        heatmap_points.sort(key=lambda x: x.count, reverse=True)
        return heatmap_points[:max_points]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理轨迹热力图数据失败: {str(e)}")

@taxi_data_router.get("/taxi/cluster-analysis", response_model=Dict[str, ClusterInfo])
async def get_cluster_analysis(db: Session = Depends(get_db)):
    """获取聚类分析结果"""
    try:
        query = """
        SELECT pick_up_cluster,
               AVG(pick_up_latitude) as center_lat,
               AVG(pick_up_longitude) as center_lng,
               COUNT(*) as count,
               AVG(CASE 
                   WHEN pick_up_latitude IS NOT NULL AND pick_up_longitude IS NOT NULL 
                        AND drop_off_latitude IS NOT NULL AND drop_off_longitude IS NOT NULL
                   THEN 6371 * acos(cos(radians(pick_up_latitude)) * cos(radians(drop_off_latitude)) 
                        * cos(radians(drop_off_longitude) - radians(pick_up_longitude)) 
                        + sin(radians(pick_up_latitude)) * sin(radians(drop_off_latitude)))
                   ELSE NULL
               END) as avg_distance
        FROM taxi_od_clusters
        WHERE pick_up_cluster != -1 
              AND pick_up_latitude IS NOT NULL 
              AND pick_up_longitude IS NOT NULL
        GROUP BY pick_up_cluster
        HAVING COUNT(*) > 5
        ORDER BY count DESC
        LIMIT 1000
        """
        
        result = db.execute(text(query))
        rows = result.fetchall()
        
        cluster_result = {}
        for row in rows:
            cluster_id = str(row[0])
            cluster_result[cluster_id] = ClusterInfo(
                center_latitude=float(row[1]),
                center_longitude=float(row[2]),
                count=int(row[3]),
                avg_distance_km=float(row[4]) if row[4] else 0.0,
                avg_duration_minutes=0.0  # 需要根据实际数据计算
            )
        
        return cluster_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取聚类分析数据失败: {str(e)}")

@taxi_data_router.get("/taxi/time-analysis", response_model=List[TimeStats])
async def get_time_analysis(db: Session = Depends(get_db)):
    """获取时间统计分析"""
    try:
        query = """
        SELECT 
            EXTRACT(HOUR FROM TO_TIMESTAMP(pick_up_timestamp, 'YYYY/MM/DD HH24:MI')) as hour,
            COUNT(DISTINCT vehicle_id) as vehicle_count,
            AVG(CASE 
                WHEN pick_up_latitude IS NOT NULL AND pick_up_longitude IS NOT NULL 
                     AND drop_off_latitude IS NOT NULL AND drop_off_longitude IS NOT NULL
                THEN 6371 * acos(cos(radians(pick_up_latitude)) * cos(radians(drop_off_latitude)) 
                     * cos(radians(drop_off_longitude) - radians(pick_up_longitude)) 
                     + sin(radians(pick_up_latitude)) * sin(radians(drop_off_latitude)))
                ELSE NULL
            END) as avg_distance
        FROM taxi_od_clusters
        WHERE pick_up_timestamp IS NOT NULL
        GROUP BY EXTRACT(HOUR FROM TO_TIMESTAMP(pick_up_timestamp, 'YYYY/MM/DD HH24:MI'))
        ORDER BY hour
        LIMIT 24
        """
        
        result = db.execute(text(query))
        rows = result.fetchall()
        
        time_stats = []
        for row in rows:
            stats = TimeStats(
                hour=int(row[0]),
                vehicle_count=int(row[1]),
                avg_distance=float(row[2]) if row[2] else 0.0,
                avg_duration=float(row[3]) if row[3] else 0.0  # 修复：使用row[3]并删除重复行
            )
            time_stats.append(stats)
        
        return time_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取时间分析数据失败: {str(e)}")

@taxi_data_router.get("/taxi/od-data")
async def get_od_data(
    limit: Optional[int] = 1000,
    db: Session = Depends(get_db)
):
    """获取OD数据 - 用于轨迹可视化"""
    try:
        query = """
        SELECT vehicle_id, pick_up_timestamp, pick_up_latitude, pick_up_longitude,
               drop_off_timestamp, drop_off_latitude, drop_off_longitude, pick_up_cluster
        FROM taxi_od_clusters
        WHERE pick_up_latitude IS NOT NULL AND pick_up_longitude IS NOT NULL
              AND drop_off_latitude IS NOT NULL AND drop_off_longitude IS NOT NULL
        ORDER BY pick_up_timestamp
        LIMIT :limit
        """
        
        result = db.execute(text(query), {'limit': limit})
        rows = result.fetchall()
        
        od_data = []
        for row in rows:
            od_data.append({
                'vehicle_id': row[0],
                'pick_up_timestamp': row[1],
                'pick_up_latitude': row[2],
                'pick_up_longitude': row[3],
                'drop_off_timestamp': row[4],
                'drop_off_latitude': row[5],
                'drop_off_longitude': row[6],
                'pick_up_cluster': row[7]
            })
        
        return od_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取OD数据失败: {str(e)}")

@taxi_data_router.get("/taxi/trajectory-data")
async def get_trajectory_data(
    vehicle_id: Optional[str] = None, 
    limit: Optional[int] = 5000,
    db: Session = Depends(get_db)
):
    """获取轨迹数据"""
    try:
        query = """
        SELECT vehicle_id, timestamp, latitude_bd09, longitude_bd09, 
               heading, speed, occupied
        FROM cleaned_taxi_trajectory
        WHERE latitude_bd09 IS NOT NULL AND longitude_bd09 IS NOT NULL
        """
        
        params = {'limit': limit}
        
        # 如果指定了车辆ID，则过滤
        if vehicle_id:
            query += " AND vehicle_id = :vehicle_id"
            params['vehicle_id'] = vehicle_id
        
        query += " ORDER BY timestamp LIMIT :limit"
        
        result = db.execute(text(query), params)
        rows = result.fetchall()
        
        trajectory_data = []
        for row in rows:
            trajectory_data.append({
                'vehicle_id': row[0],
                'timestamp': row[1],
                'latitude_bd09': row[2],
                'longitude_bd09': row[3],
                'heading': row[4],
                'speed': row[5],
                'occupied': row[6]
            })
        
        return trajectory_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取轨迹数据失败: {str(e)}")



@taxi_data_router.get("/taxi/heatmap-data", response_model=List[HeatmapPoint])
async def get_heatmap_data(
    start_hour: Optional[int] = Query(None, ge=0, le=23, description="起始小时 (0-23)"),
    end_hour: Optional[int] = Query(None, ge=0, le=23, description="结束小时 (0-23)"),
    db: Session = Depends(get_db)
):
    """获取热力图数据 - 基于聚类中心，支持时间过滤"""
    try:
        # 构建时间过滤条件
        time_filter = ""
        params = {}
        
        if start_hour is not None and end_hour is not None:
            if start_hour <= end_hour:
                time_filter = "AND EXTRACT(HOUR FROM TO_TIMESTAMP(pick_up_timestamp, 'YYYY/MM/DD HH24:MI')) BETWEEN :start_hour AND :end_hour"
            else:  # 跨天情况
                time_filter = "AND (EXTRACT(HOUR FROM TO_TIMESTAMP(pick_up_timestamp, 'YYYY/MM/DD HH24:MI')) >= :start_hour OR EXTRACT(HOUR FROM TO_TIMESTAMP(pick_up_timestamp, 'YYYY/MM/DD HH24:MI')) <= :end_hour)"
            
            params['start_hour'] = start_hour
            params['end_hour'] = end_hour
        
        # 基于聚类中心生成热力图
        query = f"""
        SELECT pick_up_cluster, 
               AVG(pick_up_latitude) as center_lat,
               AVG(pick_up_longitude) as center_lng,
               COUNT(*) as count
        FROM taxi_od_clusters
        WHERE pick_up_cluster != -1 
              AND pick_up_latitude IS NOT NULL 
              AND pick_up_longitude IS NOT NULL
              {time_filter}
        GROUP BY pick_up_cluster
        HAVING COUNT(*) > 5
        ORDER BY count DESC
        LIMIT 5000
        """
        
        result = db.execute(text(query), params)
        rows = result.fetchall()
        
        heatmap_points = []
        for row in rows:
            point = HeatmapPoint(
                lng=float(row[2]),
                lat=float(row[1]),
                count=int(row[3])
            )
            heatmap_points.append(point)
        
        return heatmap_points
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取聚类数据失败: {str(e)}")

@taxi_data_router.get("/taxi/time-range-stats")
async def get_time_range_stats(
    start_hour: int = Query(..., ge=0, le=23, description="起始小时 (0-23)"),
    end_hour: int = Query(..., ge=0, le=23, description="结束小时 (0-23)"),
    db: Session = Depends(get_db)
):
    """获取指定时间范围的统计信息"""
    try:
        # 构建时间过滤条件
        if start_hour <= end_hour:
            time_filter = "AND EXTRACT(HOUR FROM TO_TIMESTAMP(pick_up_timestamp, 'YYYY/MM/DD HH24:MI')) BETWEEN :start_hour AND :end_hour"
        else:  # 跨天情况
            time_filter = "AND (EXTRACT(HOUR FROM TO_TIMESTAMP(pick_up_timestamp, 'YYYY/MM/DD HH24:MI')) >= :start_hour OR EXTRACT(HOUR FROM TO_TIMESTAMP(pick_up_timestamp, 'YYYY/MM/DD HH24:MI')) <= :end_hour)"
        
        query = f"""
        SELECT 
            COUNT(DISTINCT vehicle_id) as total_vehicles,
            AVG(CASE 
                WHEN pick_up_latitude IS NOT NULL AND pick_up_longitude IS NOT NULL 
                     AND drop_off_latitude IS NOT NULL AND drop_off_longitude IS NOT NULL
                THEN 6371 * acos(cos(radians(pick_up_latitude)) * cos(radians(drop_off_latitude)) 
                     * cos(radians(drop_off_longitude) - radians(pick_up_longitude)) 
                     + sin(radians(pick_up_latitude)) * sin(radians(drop_off_latitude)))
                ELSE NULL
            END) as avg_distance
        FROM taxi_od_clusters
        WHERE 1=1 {time_filter}
        LIMIT 50000
        """
        
        result = db.execute(text(query), {
            'start_hour': start_hour,
            'end_hour': end_hour
        })
        
        row = result.fetchone()
        
        # 处理跨天的时间范围
        if start_hour <= end_hour:
            hours = list(range(start_hour, end_hour + 1))
        else:  # 跨天情况
            hours = list(range(start_hour, 24)) + list(range(0, end_hour + 1))
        
        return {
            "time_range": f"{start_hour:02d}:00 - {end_hour:02d}:59",
            "total_vehicles": row[0] if row[0] else 0,
            "avg_distance": round(row[1], 2) if row[1] else 0,
            "avg_duration": 0,  # 需要根据实际数据计算
            "hours_included": hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取时间统计数据失败: {str(e)}")

@taxi_data_router.get("/taxi/data-distribution")
async def get_data_distribution(db: Session = Depends(get_db)):
    """获取数据地理分布统计"""
    try:
        query = """
        SELECT 
            MIN(latitude_bd09) as lat_min,
            MAX(latitude_bd09) as lat_max,
            MIN(longitude_bd09) as lng_min,
            MAX(longitude_bd09) as lng_max,
            AVG(latitude_bd09) as lat_avg
        FROM cleaned_taxi_trajectory
        WHERE latitude_bd09 IS NOT NULL AND longitude_bd09 IS NOT NULL
        LIMIT 100000
        """
        
        result = db.execute(text(query))
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="没有找到轨迹数据")
        
        lat_min, lat_max, lng_min, lng_max, lat_avg = row
        
        # 按纬度分区统计
        count_query = """
        SELECT 
            SUM(CASE WHEN latitude_bd09 > :lat_avg THEN 1 ELSE 0 END) as north_count,
            SUM(CASE WHEN latitude_bd09 <= :lat_avg THEN 1 ELSE 0 END) as south_count,
            COUNT(*) as total_count
        FROM cleaned_taxi_trajectory
        WHERE latitude_bd09 IS NOT NULL AND longitude_bd09 IS NOT NULL
        LIMIT 100000
        """
        
        count_result = db.execute(text(count_query), {'lat_avg': lat_avg})
        count_row = count_result.fetchone()
        
        north_count, south_count, total_count = count_row
        
        return {
            "coordinate_range": {
                "lat_min": lat_min,
                "lat_max": lat_max,
                "lng_min": lng_min,
                "lng_max": lng_max
            },
            "distribution": {
                "north_count": north_count,
                "south_count": south_count,
                "north_percentage": round(north_count / total_count * 100, 2) if total_count > 0 else 0,
                "south_percentage": round(south_count / total_count * 100, 2) if total_count > 0 else 0
            },
            "total_points": total_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据分布失败: {str(e)}")

@taxi_data_router.get("/taxi/heatmap-data-fast", response_model=List[HeatmapPoint])
async def get_heatmap_data_fast(
    max_points: Optional[int] = Query(5000, description="最大返回点数"),
    db: Session = Depends(get_db)
):
    """快速热力图数据 - 使用聚类分析"""
    try:
        # 从数据库获取聚类数据
        query = """
        SELECT 
            pick_up_cluster as cluster_id,
            AVG(pick_up_latitude) as center_latitude,
            AVG(pick_up_longitude) as center_longitude,
            COUNT(*) as count
        FROM taxi_od_clusters
        WHERE pick_up_cluster IS NOT NULL
        AND pick_up_cluster != '-1'
        GROUP BY pick_up_cluster
        ORDER BY count DESC
        LIMIT :max_points
        """
        
        result = db.execute(text(query), {"max_points": max_points})
        rows = result.fetchall()
        
        heatmap_points = []
        for row in rows:
            cluster_id, center_latitude, center_longitude, count = row
            if cluster_id != "-1":  # 排除噪声点
                point = HeatmapPoint(
                    lng=float(center_longitude),
                    lat=float(center_latitude),
                    count=count
                )
                heatmap_points.append(point)
        
        return heatmap_points
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取快速热力图数据失败: {str(e)}")

@taxi_data_router.get("/taxi/trajectory-heatmap-data", response_model=List[HeatmapPoint])
async def get_trajectory_heatmap_data(
    sample_rate: Optional[float] = Query(0.03, description="采样率 (0.01-1.0)"),
    grid_size: Optional[float] = Query(0.005, description="网格大小 (度)"),
    max_points: Optional[int] = Query(6000, description="最大返回点数"),
    db: Session = Depends(get_db)
):
    """获取基于原始轨迹数据的热力图数据 - 性能优化版本"""
    try:
        # 使用随机采样来减少数据量
        query = """
        SELECT latitude_bd09, longitude_bd09
        FROM cleaned_taxi_trajectory
        WHERE latitude_bd09 IS NOT NULL AND longitude_bd09 IS NOT NULL
              AND random() < :sample_rate
        LIMIT 50000
        """
        
        result = db.execute(text(query), {'sample_rate': sample_rate})
        rows = result.fetchall()
        
        # 网格聚合
        grid_dict = {}
        for row in rows:
            lat, lng = row[0], row[1]
            grid_lat = round(lat / grid_size) * grid_size
            grid_lng = round(lng / grid_size) * grid_size
            grid_key = (grid_lat, grid_lng)
            
            if grid_key in grid_dict:
                grid_dict[grid_key] += 1
            else:
                grid_dict[grid_key] = 1
        
        # 转换为热力图点
        heatmap_points = []
        for (lat, lng), count in grid_dict.items():
            point = HeatmapPoint(
                lng=float(lng),
                lat=float(lat),
                count=count
            )
            heatmap_points.append(point)
        
        # 按权重排序并限制返回数量
        heatmap_points.sort(key=lambda x: x.count, reverse=True)
        return heatmap_points[:max_points]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取轨迹热力图数据失败: {str(e)}")

@taxi_data_router.get("/taxi/trajectory-heatmap-data", response_model=List[HeatmapPoint])
async def get_trajectory_heatmap_data(
    sample_rate: Optional[float] = Query(0.03, description="采样率 (0.01-1.0)"),
    grid_size: Optional[float] = Query(0.005, description="网格大小 (度)"),
    max_points: Optional[int] = Query(6000, description="最大返回点数"),
    db: Session = Depends(get_db)
):
    """获取基于原始轨迹数据的热力图数据 - 性能优化版本"""
    try:
        # 使用随机采样来减少数据量
        query = """
        SELECT latitude_bd09, longitude_bd09
        FROM cleaned_taxi_trajectory
        WHERE latitude_bd09 IS NOT NULL AND longitude_bd09 IS NOT NULL
              AND random() < :sample_rate
        LIMIT 50000
        """
        
        result = db.execute(text(query), {'sample_rate': sample_rate})
        rows = result.fetchall()
        
        # 网格聚合
        grid_dict = {}
        for row in rows:
            lat, lng = row[0], row[1]
            grid_lat = round(lat / grid_size) * grid_size
            grid_lng = round(lng / grid_size) * grid_size
            grid_key = (grid_lat, grid_lng)
            
            if grid_key in grid_dict:
                grid_dict[grid_key] += 1
            else:
                grid_dict[grid_key] = 1
        
        # 转换为热力图点
        heatmap_points = []
        for (lat, lng), count in grid_dict.items():
            point = HeatmapPoint(
                lng=float(lng),
                lat=float(lat),
                count=count
            )
            heatmap_points.append(point)
        
        # 按权重排序并限制返回数量
        heatmap_points.sort(key=lambda x: x.count, reverse=True)
        return heatmap_points[:max_points]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理轨迹热力图数据失败: {str(e)}")

@taxi_data_router.get("/taxi/heatmap-data-adaptive", response_model=List[HeatmapPoint])
async def get_heatmap_data_adaptive(
    start_utc: Optional[str] = Query(None, description="起始UTC时间 (格式: YYYY-MM-DD HH:MM:SS)"),
    end_utc: Optional[str] = Query(None, description="结束UTC时间 (格式: YYYY-MM-DD HH:MM:SS)"),
    max_points: Optional[int] = Query(15000, description="最大返回点数"),
    preserve_sparse: Optional[bool] = Query(True, description="是否保留稀疏区域数据")
):
    """自适应网格聚合热力图 - 保留低密度区域数据"""
    try:
        trajectory_file = os.path.join(DATA_DIR, 'cleaned_taxi_trajectory.csv')
        
        # 第一阶段：密度分析
        density_grid = {}  # 用于分析区域密度
        coarse_grid_size = 0.005  # 粗网格用于密度分析
        
        chunk_size = 30000
        sample_rate = 0.15  # 提高采样率以更好保留稀疏区域
        
        # 密度分析阶段
        for chunk in pd.read_csv(trajectory_file, chunksize=chunk_size):
            chunk = chunk.sample(frac=0.05, random_state=42)  # 快速密度分析
            
            # 时间过滤
            if start_utc and end_utc:
                chunk['timestamp'] = pd.to_datetime(chunk['timestamp'], format='%Y/%m/%d %H:%M:%S')
                chunk['utc_time'] = chunk['timestamp'] - pd.Timedelta(hours=8)
                start_time = pd.to_datetime(start_utc)
                end_time = pd.to_datetime(end_utc)
                start_time = pd.to_datetime(start_utc)
                end_time = pd.to_datetime(end_utc)
                chunk = chunk[(chunk['utc_time'] >= start_time) & (chunk['utc_time'] <= end_time)]
            
            # 粗网格密度统计
            for _, row in chunk.iterrows():
                grid_lat = round(row['latitude_bd09'] / coarse_grid_size) * coarse_grid_size
                grid_lng = round(row['longitude_bd09'] / coarse_grid_size) * coarse_grid_size
                grid_key = (grid_lat, grid_lng)
                density_grid[grid_key] = density_grid.get(grid_key, 0) + 1
        
        # 计算密度阈值
        densities = list(density_grid.values())
        if densities:
            density_threshold = np.percentile(densities, 25)  # 25%分位数作为低密度阈值
        else:
            density_threshold = 1
        
        # 第二阶段：自适应聚合
        fine_grid_dict = {}    # 高密度区域用细网格
        coarse_grid_dict = {}  # 低密度区域用粗网格
        sparse_points = []     # 极稀疏区域保留原始点
        
        processed_count = 0
        max_process = 600000
        
        for chunk in pd.read_csv(trajectory_file, chunksize=chunk_size):
            if processed_count >= max_process:
                break
                
            chunk = chunk.sample(frac=sample_rate, random_state=42)
            
            # 时间过滤
            if start_utc and end_utc:
                chunk['timestamp'] = pd.to_datetime(chunk['timestamp'], format='%Y/%m/%d %H:%M:%S')
                chunk['utc_time'] = chunk['timestamp'] - pd.Timedelta(hours=8)
                start_time = pd.to_datetime(start_utc)
                end_time = pd.to_datetime(end_utc)
                start_time = pd.to_datetime(start_utc)
                end_time = pd.to_datetime(end_utc)
                chunk = chunk[(chunk['utc_time'] >= start_time) & (chunk['utc_time'] <= end_time)]
            
            for _, row in chunk.iterrows():
                # 判断当前点所在区域的密度
                coarse_lat = round(row['latitude_bd09'] / coarse_grid_size) * coarse_grid_size
                coarse_lng = round(row['longitude_bd09'] / coarse_grid_size) * coarse_grid_size
                region_density = density_grid.get((coarse_lat, coarse_lng), 0)
                
                if region_density > density_threshold * 3:  # 高密度区域
                    # 使用细网格聚合
                    fine_grid_size = 0.0005
                    grid_lat = round(row['latitude_bd09'] / fine_grid_size) * fine_grid_size
                    grid_lng = round(row['longitude_bd09'] / fine_grid_size) * fine_grid_size
                    grid_key = (grid_lat, grid_lng)
                    fine_grid_dict[grid_key] = fine_grid_dict.get(grid_key, 0) + 1
                    
                elif region_density > density_threshold:  # 中密度区域
                    # 使用中等网格聚合
                    medium_grid_size = 0.002
                    grid_lat = round(row['latitude_bd09'] / medium_grid_size) * medium_grid_size
                    grid_lng = round(row['longitude_bd09'] / medium_grid_size) * medium_grid_size
                    grid_key = (grid_lat, grid_lng)
                    coarse_grid_dict[grid_key] = coarse_grid_dict.get(grid_key, 0) + 1
                    
                else:  # 低密度区域
                    if preserve_sparse:
                        # 保留原始点，不进行聚合
                        sparse_points.append({
                            'lat': float(row['latitude_bd09']),
                            'lng': float(row['longitude_bd09']),
                            'count': 1
                        })
            
            processed_count += len(chunk)
        
        # 合并所有热力图点
        heatmap_points = []
        
        # 添加高密度区域点
        for (lat, lng), count in fine_grid_dict.items():
            heatmap_points.append(HeatmapPoint(lng=float(lng), lat=float(lat), count=count))
        
        # 添加中密度区域点
        for (lat, lng), count in coarse_grid_dict.items():
            heatmap_points.append(HeatmapPoint(lng=float(lng), lat=float(lat), count=count))
        
        # 添加稀疏区域原始点
        for point in sparse_points:
            heatmap_points.append(HeatmapPoint(
                lng=point['lng'], 
                lat=point['lat'], 
                count=point['count']
            ))
        
        # 先保留稀疏区域点
        def sort_key(point):
            # 稀疏区域点（count=1）优先级最高
            if point.count == 1:
                return (0, -point.count)  # 优先级0，按count降序
            else:
                return (1, -point.count)  # 优先级1，按count降序
        
        heatmap_points.sort(key=sort_key)
        
        # 确保稀疏区域点不被截断
        sparse_count = len(sparse_points)
        if len(heatmap_points) > max_points:
            # 保留所有稀疏点 + 部分聚合点
            result = heatmap_points[:sparse_count]  # 所有稀疏点
            remaining_quota = max_points - sparse_count
            if remaining_quota > 0:
                # 添加权重最高的聚合点
                aggregated_points = [p for p in heatmap_points if p.count > 1]
                aggregated_points.sort(key=lambda x: x.count, reverse=True)
                result.extend(aggregated_points[:remaining_quota])
            return result
        else:
            return heatmap_points
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"自适应聚合处理失败: {str(e)}")

# 基于完整轨迹数据的热力图API
@taxi_data_router.get("/taxi/heatmap-data-full-trajectory", response_model=List[HeatmapPoint])
async def get_heatmap_data_full_trajectory(
    max_points: Optional[int] = Query(15000, description="最大返回点数"),
    grid_size: Optional[float] = Query(0.005, description="网格聚合大小(度)"),
    sample_rate: Optional[float] = Query(0.15, description="数据采样率"),
    db: Session = Depends(get_db)
):
    """基于完整轨迹数据生成热力图"""
    try:
        # 从数据库获取轨迹数据
        query = """
        SELECT latitude_bd09, longitude_bd09
        FROM cleaned_taxi_trajectory
        WHERE latitude_bd09 IS NOT NULL AND longitude_bd09 IS NOT NULL
        AND random() < :sample_rate
        LIMIT 1000000
        """
        
        result = db.execute(text(query), {"sample_rate": sample_rate})
        
        # 网格聚合字典
        grid_dict = {}
        
        # 处理查询结果
        for row in result:
            try:
                lat = float(row[0])
                lng = float(row[1])
                
                # 网格聚合
                grid_lat = round(lat / grid_size) * grid_size
                grid_lng = round(lng / grid_size) * grid_size
                grid_key = (grid_lat, grid_lng)
                
                grid_dict[grid_key] = grid_dict.get(grid_key, 0) + 1
                
            except (ValueError, KeyError) as e:
                # 跳过无效数据
                continue
        
        # 转换为热力图点
        heatmap_points = []
        for (lat, lng), count in grid_dict.items():
            point = HeatmapPoint(
                lng=float(lng),
                lat=float(lat),
                count=count
            )
            heatmap_points.append(point)
        
        # 按权重排序并限制数量
        heatmap_points.sort(key=lambda x: x.count, reverse=True)
        
        return heatmap_points[:max_points]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取完整轨迹数据失败: {str(e)}")

# 在文件末尾添加以下新的API

# 基于OD数据的热力图API
@taxi_data_router.get("/taxi/heatmap-data-od", response_model=List[HeatmapPoint])
async def get_heatmap_data_od(
    max_points: Optional[int] = Query(2000, description="最大返回点数"),
    use_pickup: Optional[bool] = Query(True, description="是否使用上车点（否则使用下车点）"),
    grid_size: Optional[float] = Query(0.01, description="网格聚合大小(度)"),
    db: Session = Depends(get_db)
):
    """基于OD数据生成热力图"""
    try:
        # 选择使用上车点还是下车点
        if use_pickup:
            lat_col = "pick_up_latitude"
            lng_col = "pick_up_longitude"
        else:
            lat_col = "drop_off_latitude"
            lng_col = "drop_off_longitude"
        
        # 从数据库获取OD数据
        query = f"""
        SELECT {lat_col}, {lng_col}
        FROM taxi_od_clusters
        WHERE {lat_col} IS NOT NULL AND {lng_col} IS NOT NULL
        LIMIT 200000
        """
        
        result = db.execute(text(query))
        
        # 网格聚合处理
        grid_dict = {}
        for row in result:
            try:
                lat = float(row[0])
                lng = float(row[1])
                
                # 网格聚合
                grid_lat = round(lat / grid_size) * grid_size
                grid_lng = round(lng / grid_size) * grid_size
                grid_key = (grid_lat, grid_lng)
                
                grid_dict[grid_key] = grid_dict.get(grid_key, 0) + 1
                
            except (ValueError, KeyError) as e:
                continue
        
        # 转换为热力图点
        heatmap_points = []
        for (lat, lng), count in grid_dict.items():
            point = HeatmapPoint(
                lng=float(lng),
                lat=float(lat),
                count=count
            )
            heatmap_points.append(point)
        
        # 按权重排序并限制数量
        heatmap_points.sort(key=lambda x: x.count, reverse=True)
        return heatmap_points[:max_points]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取OD热力图数据失败: {str(e)}")

# 基于聚类数据的热力图API
@taxi_data_router.get("/taxi/heatmap-data-clusters", response_model=List[HeatmapPoint])
async def get_heatmap_data_clusters(
    max_points: Optional[int] = Query(1000, description="最大返回点数"),
    grid_size: Optional[float] = Query(0.005, description="网格聚合大小(度)"),
    db: Session = Depends(get_db)
):
    """基于聚类数据生成热力图 - 使用上客点数据"""
    try:
        # 从数据库获取聚类数据
        query = """
        SELECT pick_up_latitude, pick_up_longitude
        FROM taxi_od_clusters
        WHERE pick_up_latitude IS NOT NULL AND pick_up_longitude IS NOT NULL
        LIMIT 200000
        """
        
        result = db.execute(text(query))
        
        # 网格聚合处理
        grid_dict = {}
        for row in result:
            try:
                lat = float(row[0])
                lng = float(row[1])
                
                # 网格聚合
                grid_lat = round(lat / grid_size) * grid_size
                grid_lng = round(lng / grid_size) * grid_size
                grid_key = (grid_lat, grid_lng)
                
                grid_dict[grid_key] = grid_dict.get(grid_key, 0) + 1
                
            except (ValueError, KeyError) as e:
                # 跳过无效数据
                continue
        
        # 转换为热力图点
        heatmap_points = []
        for (lat, lng), count in grid_dict.items():
            point = HeatmapPoint(
                lng=float(lng),
                lat=float(lat),
                count=count
            )
            heatmap_points.append(point)
        
        # 按权重排序并限制数量
        heatmap_points.sort(key=lambda x: x.count, reverse=True)
        return heatmap_points[:max_points]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取聚类热力图数据失败: {str(e)}")

# 密集上客点查询API
@taxi_data_router.get("/taxi/heatmap-data-cluster", response_model=List[HeatmapPoint])
@api_exception_handler("获取密集上客区域数据失败")
async def get_heatmap_data_cluster(
    max_points: Optional[int] = Query(50, description="最大返回点数"),
    grid_size: Optional[float] = Query(0.005, description="网格聚合大小(度)"),
    db: Session = Depends(get_db)
):
    """获取密集上客区域数据 - 返回上客次数最多的区域"""
    # 从数据库获取上客点数据
    query = """
    SELECT pick_up_latitude, pick_up_longitude, COUNT(*) as pickup_count
    FROM taxi_od_clusters
    WHERE pick_up_latitude IS NOT NULL AND pick_up_longitude IS NOT NULL
    GROUP BY pick_up_latitude, pick_up_longitude
    ORDER BY pickup_count DESC
    LIMIT 1000
    """
    
    result = db.execute(text(query))
    
    # 使用通用函数处理数据，指定计数字段索引为2
    grid_dict = aggregate_grid_data(result, grid_size, count_field_index=2)
    return convert_to_heatmap_points(grid_dict, max_points)

# 混合热力图API - 结合OD和聚类数据
@taxi_data_router.get("/taxi/heatmap-data-mixed", response_model=List[HeatmapPoint])
async def get_heatmap_data_mixed(
    max_points: Optional[int] = Query(1500, description="最大返回点数"),
    od_ratio: Optional[float] = Query(0.7, description="OD数据占比 (0.0-1.0)"),
    grid_size: Optional[float] = Query(0.01, description="网格聚合大小(度)")
):
    """混合热力图数据 - 结合OD数据和聚类数据"""
    try:
        od_points_limit = int(max_points * od_ratio)
        cluster_points_limit = max_points - od_points_limit
        
        # 获取OD数据点
        od_points = await get_heatmap_data_od(max_points=od_points_limit, grid_size=grid_size)
        
        # 获取聚类数据点
        cluster_points = await get_heatmap_data_clusters(max_points=cluster_points_limit)
        
        # 合并数据
        all_points = list(od_points) + list(cluster_points)
        
        # 按权重排序
        all_points.sort(key=lambda x: x.count, reverse=True)
        
        return all_points[:max_points]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"混合热力图数据处理失败: {str(e)}")