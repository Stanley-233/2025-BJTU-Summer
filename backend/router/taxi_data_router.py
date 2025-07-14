from datetime import datetime, timezone
import json
import os
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

taxi_data_router = APIRouter()

# 数据文件路径
DATA_DIR = r"d:\mine\bjtu\software engineering7\2025-BJTU-Summer-main\2025-BJTU-Summer-main\cleaned_jn0912"

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

# 新增：UTC时间范围热力图数据API
@taxi_data_router.get("/taxi/heatmap-data-utc", response_model=List[HeatmapPoint])
async def get_heatmap_data_utc(
    start_utc: Optional[str] = Query(None, description="起始UTC时间 (格式: YYYY-MM-DD HH:MM:SS)"),
    end_utc: Optional[str] = Query(None, description="结束UTC时间 (格式: YYYY-MM-DD HH:MM:SS)")
):
    """获取热力图数据 - 基于UTC时间范围过滤"""
    try:
        # 读取原始轨迹数据
        trajectory_file = os.path.join(DATA_DIR, 'cleaned_taxi_trajectory.csv')
        
        # 使用分块读取大文件
        chunk_list = []
        chunk_size = 50000
        
        # 在 get_heatmap_data_utc 函数中 (大约第50行)
        for chunk in pd.read_csv(trajectory_file, chunksize=chunk_size):
            # 移除强制列名映射，直接使用CSV文件的原始列名
            # if len(chunk.columns) >= 7:
            #     chunk.columns = ['vehicle_id', 'timestamp', 'longitude', 'latitude', 'col_e', 'col_f', 'occupied']
            
            # 转换时间戳为UTC时间 - 修复时间格式
            chunk['timestamp'] = pd.to_datetime(chunk['timestamp'], format='%Y-%m-%d %H:%M:%S')
            chunk['utc_time'] = chunk['timestamp'] - pd.Timedelta(hours=8)
            
            # 如果指定了时间范围，进行过滤
            if start_utc and end_utc:
                start_time = pd.to_datetime(start_utc)
                end_time = pd.to_datetime(end_utc)
                chunk = chunk[(chunk['utc_time'] >= start_time) & (chunk['utc_time'] <= end_time)]
            
            if len(chunk) > 0:
                chunk_list.append(chunk)
        
        if not chunk_list:
            return []
        
        # 合并所有符合条件的数据
        filtered_data = pd.concat(chunk_list, ignore_index=True)
        
        # 只保留载客状态为1的数据（上客点）
        pickup_data = filtered_data[filtered_data['occupied'] == 1]
        
        if len(pickup_data) == 0:
            return []
        
        # 对上客点进行简单的网格聚合（0.001度约100米）
        grid_size = 0.001
        pickup_data['lat_grid'] = (pickup_data['latitude'] / grid_size).round() * grid_size
        pickup_data['lng_grid'] = (pickup_data['longitude'] / grid_size).round() * grid_size
        
        # 按网格聚合计数
        grid_counts = pickup_data.groupby(['lat_grid', 'lng_grid']).size().reset_index(name='count')
        
        # 转换为热力图点格式
        heatmap_points = []
        for _, row in grid_counts.iterrows():
            if row['count'] >= 5:  # 只显示有足够数据点的网格
                point = HeatmapPoint(
                    lng=float(row['lng_grid']),
                    lat=float(row['lat_grid']),
                    count=int(row['count'])
                )
                heatmap_points.append(point)
        
        return heatmap_points[:1000]  # 限制返回数量以提高性能
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理UTC时间范围数据失败: {str(e)}")

# 新增：获取UTC时间范围统计信息
@taxi_data_router.get("/taxi/utc-time-stats")
async def get_utc_time_stats(
    start_utc: str = Query(..., description="起始UTC时间 (格式: YYYY-MM-DD HH:MM:SS)"),
    end_utc: str = Query(..., description="结束UTC时间 (格式: YYYY-MM-DD HH:MM:SS)")
):
    """获取指定UTC时间范围的统计信息"""
    try:
        # 读取OD数据进行统计
        od_file = os.path.join(DATA_DIR, 'cleaned_od_data.csv')
        
        # 分块读取OD数据
        chunk_list = []
        chunk_size = 10000
        
        for chunk in pd.read_csv(od_file, chunksize=chunk_size):
            # 转换时间戳
            chunk['pick_up_timestamp'] = pd.to_datetime(chunk['pick_up_timestamp'])
            chunk['utc_pickup_time'] = chunk['pick_up_timestamp'] - pd.Timedelta(hours=8)
            
            # 时间范围过滤
            start_time = pd.to_datetime(start_utc)
            end_time = pd.to_datetime(end_utc)
            chunk = chunk[(chunk['utc_pickup_time'] >= start_time) & (chunk['utc_pickup_time'] <= end_time)]
            
            if len(chunk) > 0:
                chunk_list.append(chunk)
        
        if not chunk_list:
            return {
                "time_range": f"{start_utc} - {end_utc} (UTC)",
                "total_trips": 0,
                "unique_vehicles": 0,
                "avg_distance": 0,
                "avg_duration": 0
            }
        
        filtered_od = pd.concat(chunk_list, ignore_index=True)
        
        return {
            "time_range": f"{start_utc} - {end_utc} (UTC)",
            "total_trips": len(filtered_od),
            "unique_vehicles": filtered_od['vehicle_id'].nunique(),
            "avg_distance": round(filtered_od['distance_km'].mean(), 2),
            "avg_duration": round(filtered_od['duration_minutes'].mean(), 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取UTC时间统计失败: {str(e)}")

@taxi_data_router.get("/taxi/heatmap-data", response_model=List[HeatmapPoint])
async def get_heatmap_data(
    start_hour: Optional[int] = Query(None, ge=0, le=23, description="起始小时 (0-23)"),
    end_hour: Optional[int] = Query(None, ge=0, le=23, description="结束小时 (0-23)")
):
    """获取热力图数据 - 基于聚类中心，支持时间过滤"""
    try:
        cluster_file = os.path.join(DATA_DIR, 'cluster_analysis.json')
        time_file = os.path.join(DATA_DIR, 'time_analysis.json')
        
        with open(cluster_file, 'r', encoding='utf-8') as f:
            clusters = json.load(f)
        
        with open(time_file, 'r', encoding='utf-8') as f:
            time_data = json.load(f)
        
        # 如果指定了时间范围，计算时间权重
        time_weight = 1.0
        if start_hour is not None and end_hour is not None:
            hourly_stats = time_data['hourly_statistics']['vehicle_id_count']
            
            # 计算指定时间范围内的总活动量
            total_activity = 0
            range_activity = 0
            
            for hour in range(24):
                hour_activity = hourly_stats.get(str(hour), 0)
                total_activity += hour_activity
                
                # 处理跨天的时间范围
                if start_hour <= end_hour:
                    if start_hour <= hour <= end_hour:
                        range_activity += hour_activity
                else:  # 跨天情况，如 22:00 到 06:00
                    if hour >= start_hour or hour <= end_hour:
                        range_activity += hour_activity
            
            # 计算时间权重
            if total_activity > 0:
                time_weight = range_activity / total_activity
        
        heatmap_points = []
        for cluster_id, cluster_info in clusters.items():
            if cluster_id != "-1":  # 排除噪声点
                # 应用时间权重调整计数
                adjusted_count = int(cluster_info['count'] * time_weight)
                if adjusted_count > 0:  # 只包含有活动的点
                    point = HeatmapPoint(
                        lng=cluster_info['center_longitude'],
                        lat=cluster_info['center_latitude'],
                        count=adjusted_count
                    )
                    heatmap_points.append(point)
        
        return heatmap_points
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取聚类数据失败: {str(e)}")

@taxi_data_router.get("/taxi/time-range-stats")
async def get_time_range_stats(
    start_hour: int = Query(..., ge=0, le=23, description="起始小时 (0-23)"),
    end_hour: int = Query(..., ge=0, le=23, description="结束小时 (0-23)")
):
    """获取指定时间范围的统计信息"""
    try:
        time_file = os.path.join(DATA_DIR, 'time_analysis.json')
        with open(time_file, 'r', encoding='utf-8') as f:
            time_data = json.load(f)
        
        hourly_stats = time_data['hourly_statistics']
        
        total_vehicles = 0
        total_distance = 0
        total_duration = 0
        hour_count = 0
        
        # 处理跨天的时间范围
        if start_hour <= end_hour:
            hours = list(range(start_hour, end_hour + 1))
        else:  # 跨天情况
            hours = list(range(start_hour, 24)) + list(range(0, end_hour + 1))
        
        for hour in hours:
            hour_str = str(hour)
            if hour_str in hourly_stats['vehicle_id_count']:
                total_vehicles += hourly_stats['vehicle_id_count'][hour_str]
                total_distance += hourly_stats['distance_km_mean'].get(hour_str, 0)
                total_duration += hourly_stats['duration_minutes_mean'].get(hour_str, 0)
                hour_count += 1
        
        return {
            "time_range": f"{start_hour:02d}:00 - {end_hour:02d}:59",
            "total_vehicles": total_vehicles,
            "avg_distance": round(total_distance / hour_count, 2) if hour_count > 0 else 0,
            "avg_duration": round(total_duration / hour_count, 2) if hour_count > 0 else 0,
            "hours_included": hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取时间统计数据失败: {str(e)}")

@taxi_data_router.get("/taxi/cluster-analysis", response_model=Dict[str, ClusterInfo])
async def get_cluster_analysis():
    """获取聚类分析结果"""
    try:
        cluster_file = os.path.join(DATA_DIR, 'cluster_analysis.json')
        with open(cluster_file, 'r', encoding='utf-8') as f:
            clusters = json.load(f)
        
        # 转换为响应模型格式
        result = {}
        for cluster_id, cluster_info in clusters.items():
            if cluster_id != "-1":
                result[cluster_id] = ClusterInfo(**cluster_info)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取聚类分析数据失败: {str(e)}")

@taxi_data_router.get("/taxi/time-analysis", response_model=List[TimeStats])
async def get_time_analysis():
    """获取时间统计分析"""
    try:
        time_file = os.path.join(DATA_DIR, 'time_analysis.json')
        with open(time_file, 'r', encoding='utf-8') as f:
            time_data = json.load(f)
        
        hourly_stats = time_data['hourly_statistics']
        result = []
        
        for hour in range(24):
            hour_str = str(hour)
            if hour_str in hourly_stats['vehicle_id_count']:
                stats = TimeStats(
                    hour=hour,
                    vehicle_count=hourly_stats['vehicle_id_count'][hour_str],
                    avg_distance=hourly_stats.get('distance_km_mean', {}).get(hour_str, 0),
                    avg_duration=hourly_stats.get('duration_minutes_mean', {}).get(hour_str, 0)
                )
                result.append(stats)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取时间分析数据失败: {str(e)}")

@taxi_data_router.get("/taxi/od-data")
async def get_od_data(limit: Optional[int] = 1000):
    """获取OD数据 - 用于轨迹可视化"""
    try:
        od_file = os.path.join(DATA_DIR, 'cleaned_od_data.csv')
        df = pd.read_csv(od_file)
        
        # 限制返回数据量
        if limit:
            df = df.head(limit)
        
        # 转换为字典格式
        od_data = df.to_dict('records')
        return od_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取OD数据失败: {str(e)}")

@taxi_data_router.get("/taxi/trajectory-data")
async def get_trajectory_data(vehicle_id: Optional[str] = None, limit: Optional[int] = 5000):
    """获取轨迹数据"""
    try:
        trajectory_file = os.path.join(DATA_DIR, 'cleaned_taxi_trajectory.csv')
        df = pd.read_csv(trajectory_file)
        
        # 如果指定了车辆ID，则过滤
        if vehicle_id:
            df = df[df['vehicle_id'] == vehicle_id]
        
        # 限制返回数据量
        if limit:
            df = df.head(limit)
        
        # 转换为字典格式
        trajectory_data = df.to_dict('records')
        return trajectory_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取轨迹数据失败: {str(e)}")

@taxi_data_router.get("/taxi/vehicle-track")
async def get_vehicle_track(
    vehicle_id: str,
    start_utc: str,
    end_utc: str
):
    """获取指定车辆在指定时间范围内的轨迹数据"""
    try:
        # 读取轨迹数据文件
        trajectory_file = os.path.join(DATA_DIR, "cleaned_taxi_trajectory.csv")
        
        if not os.path.exists(trajectory_file):
            return []
        
        # 分块读取大文件
        chunk_size = 10000
        vehicle_tracks = []
        
        for chunk in pd.read_csv(trajectory_file, chunksize=chunk_size):
            # 移除强制列名映射，直接使用CSV文件的原始列名
            # if len(chunk.columns) >= 7:
            #     chunk.columns = ['vehicle_id', 'timestamp', 'longitude', 'latitude', 'col_e', 'col_f', 'occupied']
            
            # 过滤指定车辆
            vehicle_data = chunk[chunk['vehicle_id'] == vehicle_id]
            
            if not vehicle_data.empty:
                # 转换时间戳为UTC时间 - 修复时间格式
                vehicle_data['timestamp'] = pd.to_datetime(vehicle_data['timestamp'], format='%Y-%m-%d %H:%M:%S')
                vehicle_data['utc_time'] = vehicle_data['timestamp'] - pd.Timedelta(hours=8)
                
                # 过滤时间范围
                start_time = pd.to_datetime(start_utc)
                end_time = pd.to_datetime(end_utc)
                
                filtered_data = vehicle_data[
                    (vehicle_data['utc_time'] >= start_time) & 
                    (vehicle_data['utc_time'] <= end_time)
                ]
                
                if not filtered_data.empty:
                    # 转换为轨迹点格式
                    for _, row in filtered_data.iterrows():
                        vehicle_tracks.append({
                            "lng": float(row['longitude']),
                            "lat": float(row['latitude']),
                            "timestamp": row['utc_time'].isoformat(),
                            "status": int(row.get('occupied', 0))
                        })
        
        # 按时间排序
        vehicle_tracks.sort(key=lambda x: x['timestamp'])
        
        return vehicle_tracks
        
    except Exception as e:
        print(f"获取车辆轨迹数据时出错: {e}")
        return []

@taxi_data_router.get("/taxi/trajectory-heatmap-data", response_model=List[HeatmapPoint])
async def get_trajectory_heatmap_data(
    sample_rate: Optional[float] = Query(0.3, description="采样率 (0.01-1.0)"),
    grid_size: Optional[float] = Query(0.002, description="网格大小 (度)")
):
    """获取基于原始轨迹数据的热力图数据"""
    try:
        trajectory_file = os.path.join(DATA_DIR, 'cleaned_taxi_trajectory.csv')
        
        # 使用分块读取大文件
        chunk_list = []
        chunk_size = 50000
        
        for chunk in pd.read_csv(trajectory_file, chunksize=chunk_size):
            # 根据采样率随机采样
            if sample_rate < 1.0:
                chunk = chunk.sample(frac=sample_rate, random_state=42)
            
            if len(chunk) > 0:
                chunk_list.append(chunk[['latitude', 'longitude']])
        
        if not chunk_list:
            return []
        
        # 合并所有数据
        all_data = pd.concat(chunk_list, ignore_index=True)
        
        # 网格聚合
        all_data['lat_grid'] = (all_data['latitude'] / grid_size).round() * grid_size
        all_data['lng_grid'] = (all_data['longitude'] / grid_size).round() * grid_size
        
        # 按网格计数
        grid_counts = all_data.groupby(['lat_grid', 'lng_grid']).size().reset_index(name='count')
        
        # 转换为热力图点格式
        heatmap_points = []
        for _, row in grid_counts.iterrows():
            if row['count'] >= 1:  # 降低过滤阈值
                point = HeatmapPoint(
                    lng=float(row['lng_grid']),
                    lat=float(row['lat_grid']),
                    count=int(min(row['count'], 200))  # 提高最大值到200
                )
                heatmap_points.append(point)
        
        # 按密度排序，返回前5000个最密集的点
        heatmap_points.sort(key=lambda x: x.count, reverse=True)
        return heatmap_points[:5000]  # 增加返回点数
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理轨迹热力图数据失败: {str(e)}")