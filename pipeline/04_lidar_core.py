"""Fetch LiDAR 2023 DSM+DTM 500 m tiles for a bbox (EPSG:25832 / ETRS89 UTM32N, 1 m cells assumed — read from header)
and store them as compressed float32 .npz + header JSON in _dev/data/processed/lidar2023/<kind>/ (ASCII kept only in scratch).
usage: python 04_lidar_core.py 680500 4848000 682500 4850000"""
import sys, os, io, json, subprocess, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,"..")
x0,y0,x1,y1=map(int,sys.argv[1:5]); SCR=os.path.expanduser("~/scratch/lidar"); os.makedirs(SCR,exist_ok=True)
sys.argv=[sys.argv[0]]
import importlib.util
spec=importlib.util.spec_from_file_location("lt",os.path.join(HERE,"03_lidar_tiles.py"))
for kind in ("dsm","dtm"):
    out=os.path.join(ROOT,"_dev","data","processed","lidar2023",kind); os.makedirs(out,exist_ok=True)
    for x in range(x0,x1,500):
        for y in range(y0,y1,500):
            name=f"32_{x}_{y}.ASC"; dst=os.path.join(out,name.replace(".ASC",".npz"))
            if os.path.exists(dst): continue
            subprocess.run([sys.executable,os.path.join(HERE,"03_lidar_tiles.py"),"get",kind,name],check=True,
                           env=dict(os.environ,LIDAR_RAW=SCR),cwd=HERE)
            asc=os.path.join(SCR,name)
            hdr={}
            with open(asc) as f:
                for _ in range(6):
                    k,v=f.readline().split(); hdr[k.lower()]=float(v)
                a=np.loadtxt(f,dtype=np.float32)
            a[a==hdr.get("nodata_value",-9999)]=np.nan
            np.savez_compressed(dst,z=a); json.dump(hdr,open(dst.replace(".npz",".json"),"w"))
            os.remove(asc)
            print(kind,name,a.shape,np.nanmin(a),np.nanmax(a),flush=True)
