from datetime import datetime, timezone
import json
import os
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

taxi_data_router = APIRouter()

DATA_DIR = r"d:/mine/bjtu/software engineering7/2025-BJTU-Summer-main/2025-BJTU-Summer-main/cleaned_jn0912"

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

# UTC时间范围热力图API性能优化
@taxi_data_router.get("/taxi/heatmap-data-utc", response_model=List[HeatmapPoint])
async def get_heatmap_data_utc(
    start_utc: Optional[str] = Query(None, description="起始UTC时间 (格式: YYYY-MM-DD HH:MM:SS)"),
    end_utc: Optional[str] = Query(None, description="结束UTC时间 (格式: YYYY-MM-DD HH:MM:SS)"),
    max_points: Optional[int] = Query(10000, description="最大返回点数"),
    grid_size: Optional[float] = Query(0.001, description="网格聚合大小(度)")
):
    """获取热力图数据 - 基于UTC时间范围过滤，性能优化版本"""
    try:
        trajectory_file = os.path.join(DATA_DIR, 'cleaned_taxi_trajectory.csv')
        # 使用更小的分块大小和智能采样
        chunk_size = 20000
        sample_rate = 0.1  # 默认采样10%的数据
        grid_dict = {}  # 网格聚合
        
        processed_count = 0
        max_process = 500000  # 最大处理数据量
        
        for chunk in pd.read_csv(trajectory_file, chunksize=chunk_size):
            # 早期退出机制
            if processed_count >= max_process:
                break
                
            # 智能采样
            if len(chunk) > chunk_size * 0.5:
                chunk = chunk.sample(frac=sample_rate, random_state=42)
            
            # 转换时间戳为UTC时间
            chunk['timestamp'] = pd.to_datetime(chunk['timestamp'], format='%Y/%m/%d %H:%M:%S')
            chunk['utc_time'] = chunk['timestamp'] - pd.Timedelta(hours=8)
            
            # 如果指定了时间范围，进行过滤
            if start_utc and end_utc:
                start_time = pd.to_datetime(start_utc)
                end_time = pd.to_datetime(end_utc)
                chunk = chunk[(chunk['utc_time'] >= start_time) & (chunk['utc_time'] <= end_time)]
            
            # 网格聚合处理
            for _, row in chunk.iterrows():
                # 计算网格坐标
                grid_lat = round(row['latitude'] / grid_size) * grid_size
                grid_lng = round(row['longitude'] / grid_size) * grid_size
                grid_key = (grid_lat, grid_lng)
                
                if grid_key in grid_dict:
                    grid_dict[grid_key] += 1
                else:
                    grid_dict[grid_key] = 1
            
            processed_count += len(chunk)
        
        # 转换为热力图点并限制数量
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
            # 过滤指定车辆
            vehicle_data = chunk[chunk['vehicle_id'] == vehicle_id]
            
            if not vehicle_data.empty:
                # 转换时间戳为UTC时间 - 修复时间格式以适配新数据
                vehicle_data['timestamp'] = pd.to_datetime(vehicle_data['timestamp'], format='%Y/%m/%d %H:%M:%S')
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
    sample_rate: Optional[float] = Query(0.05, description="采样率 (0.01-1.0)"),
    grid_size: Optional[float] = Query(0.001, description="网格大小 (度)"),
    max_points: Optional[int] = Query(8000, description="最大返回点数")
):
    """获取基于原始轨迹数据的热力图数据 - 性能优化版本"""
    try:
        trajectory_file = os.path.join(DATA_DIR, 'cleaned_taxi_trajectory.csv')
        
        # 使用更激进的采样和网格聚合
        chunk_size = 30000
        grid_dict = {}
        processed_count = 0
        max_process = 300000  # 限制最大处理量
        
        for chunk in pd.read_csv(trajectory_file, chunksize=chunk_size):
            if processed_count >= max_process:
                break
                
            # 采样处理
            if sample_rate < 1.0:
                chunk = chunk.sample(frac=sample_rate, random_state=42)
            
            # 网格聚合
            for _, row in chunk.iterrows():
                grid_lat = round(row['latitude'] / grid_size) * grid_size
                grid_lng = round(row['longitude'] / grid_size) * grid_size
                grid_key = (grid_lat, grid_lng)
                
                if grid_key in grid_dict:
                    grid_dict[grid_key] += 1
                else:
                    grid_dict[grid_key] = 1
            
            processed_count += len(chunk)
        
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

@taxi_data_router.get("/taxi/data-distribution")
async def get_data_distribution():
    """获取数据地理分布统计"""
    try:
        trajectory_file = os.path.join(DATA_DIR, 'cleaned_taxi_trajectory.csv')
        
        # 读取部分数据进行分析
        df = pd.read_csv(trajectory_file, nrows=100000)
        
        # 计算坐标范围
        lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
        lng_min, lng_max = df['longitude'].min(), df['longitude'].max()
        
        # 按纬度分区统计
        lat_mid = (lat_min + lat_max) / 2
        north_count = len(df[df['latitude'] > lat_mid])
        south_count = len(df[df['latitude'] <= lat_mid])
        
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
                "north_percentage": round(north_count / len(df) * 100, 2),
                "south_percentage": round(south_count / len(df) * 100, 2)
            },
            "total_points": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据分布失败: {str(e)}")

# 新增：快速热力图数据API
@taxi_data_router.get("/taxi/heatmap-data-fast", response_model=List[HeatmapPoint])
async def get_heatmap_data_fast(
    max_points: Optional[int] = Query(5000, description="最大返回点数")
):
    """快速热力图数据 - 使用预处理的聚类数据"""
    try:
        cluster_file = os.path.join(DATA_DIR, 'cluster_analysis.json')
        
        with open(cluster_file, 'r', encoding='utf-8') as f:
            clusters = json.load(f)
        
        heatmap_points = []
        for cluster_id, cluster_info in clusters.items():
            if cluster_id != "-1":  # 排除噪声点
                point = HeatmapPoint(
                    lng=cluster_info['center_longitude'],
                    lat=cluster_info['center_latitude'],
                    count=cluster_info['count']
                )
                heatmap_points.append(point)
        
        # 按权重排序并限制数量
        heatmap_points.sort(key=lambda x: x.count, reverse=True)
        return heatmap_points[:max_points]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取快速热力图数据失败: {str(e)}")

# 新增：区域密度分析API
@taxi_data_router.get("/taxi/density-analysis")
async def get_density_analysis():
    """获取各区域密度分析，帮助识别稀疏区域"""
    try:
        trajectory_file = os.path.join(DATA_DIR, 'cleaned_taxi_trajectory.csv')
        
        # 读取样本数据进行密度分析
        sample_data = pd.read_csv(trajectory_file, nrows=100000)
        
        # 网格密度统计
        grid_size = 0.01  # 1km左右的网格
        density_map = {}
        
        for _, row in sample_data.iterrows():
            grid_lat = round(row['latitude'] / grid_size) * grid_size
            grid_lng = round(row['longitude'] / grid_size) * grid_size
            grid_key = (grid_lat, grid_lng)
            density_map[grid_key] = density_map.get(grid_key, 0) + 1
        
        # 分析密度分布
        densities = list(density_map.values())
        
        return {
            "total_grids": len(density_map),
            "density_stats": {
                "min": min(densities) if densities else 0,
                "max": max(densities) if densities else 0,
                "mean": np.mean(densities) if densities else 0,
                "median": np.median(densities) if densities else 0,
                "percentile_25": np.percentile(densities, 25) if densities else 0,
                "percentile_75": np.percentile(densities, 75) if densities else 0
            },
            "sparse_regions": len([d for d in densities if d < np.percentile(densities, 25)]) if densities else 0,
            "dense_regions": len([d for d in densities if d > np.percentile(densities, 75)]) if densities else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"密度分析失败: {str(e)}")

# 改进的自适应网格聚合热力图API
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
                chunk = chunk[(chunk['utc_time'] >= start_time) & (chunk['utc_time'] <= end_time)]
            
            # 粗网格密度统计
            for _, row in chunk.iterrows():
                grid_lat = round(row['latitude'] / coarse_grid_size) * coarse_grid_size
                grid_lng = round(row['longitude'] / coarse_grid_size) * coarse_grid_size
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
                chunk = chunk[(chunk['utc_time'] >= start_time) & (chunk['utc_time'] <= end_time)]
            
            for _, row in chunk.iterrows():
                # 判断当前点所在区域的密度
                coarse_lat = round(row['latitude'] / coarse_grid_size) * coarse_grid_size
                coarse_lng = round(row['longitude'] / coarse_grid_size) * coarse_grid_size
                region_density = density_grid.get((coarse_lat, coarse_lng), 0)
                
                if region_density > density_threshold * 3:  # 高密度区域
                    # 使用细网格聚合
                    fine_grid_size = 0.0005
                    grid_lat = round(row['latitude'] / fine_grid_size) * fine_grid_size
                    grid_lng = round(row['longitude'] / fine_grid_size) * fine_grid_size
                    grid_key = (grid_lat, grid_lng)
                    fine_grid_dict[grid_key] = fine_grid_dict.get(grid_key, 0) + 1
                    
                elif region_density > density_threshold:  # 中密度区域
                    # 使用中等网格聚合
                    medium_grid_size = 0.002
                    grid_lat = round(row['latitude'] / medium_grid_size) * medium_grid_size
                    grid_lng = round(row['longitude'] / medium_grid_size) * medium_grid_size
                    grid_key = (grid_lat, grid_lng)
                    coarse_grid_dict[grid_key] = coarse_grid_dict.get(grid_key, 0) + 1
                    
                else:  # 低密度区域
                    if preserve_sparse:
                        # 保留原始点，不进行聚合
                        sparse_points.append({
                            'lat': float(row['latitude']),
                            'lng': float(row['longitude']),
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
    max_points: Optional[int] = Query(20000, description="最大返回点数"),
    grid_size: Optional[float] = Query(0.001, description="网格聚合大小(度)"),
    sample_rate: Optional[float] = Query(0.2, description="数据采样率")
):
    """基于完整轨迹数据生成热力图 - 直接读取cleaned_taxi_trajectory.csv"""
    try:
        import numpy as np
        trajectory_file = os.path.join(DATA_DIR, 'cleaned_taxi_trajectory.csv')
        
        # 网格聚合字典
        grid_dict = {}
        chunk_size = 50000
        processed_count = 0
        max_process = 1000000  # 最大处理100万条数据
        
        # 分块读取轨迹数据
        for chunk in pd.read_csv(trajectory_file, chunksize=chunk_size):
            if processed_count >= max_process:
                break
                
            # 采样处理以提高性能
            if len(chunk) > chunk_size * 0.3:
                chunk = chunk.sample(frac=sample_rate, random_state=42)
            
            # 处理每个轨迹点
            for _, row in chunk.iterrows():
                try:
                    lat = float(row['latitude'])
                    lng = float(row['longitude'])
                    
                    # 网格聚合
                    grid_lat = round(lat / grid_size) * grid_size
                    grid_lng = round(lng / grid_size) * grid_size
                    grid_key = (grid_lat, grid_lng)
                    
                    grid_dict[grid_key] = grid_dict.get(grid_key, 0) + 1
                    
                except (ValueError, KeyError) as e:
                    # 跳过无效数据
                    continue
            
            processed_count += len(chunk)
        
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