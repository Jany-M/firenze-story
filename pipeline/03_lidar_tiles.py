"""List / extract members of the Comune di Firenze LiDAR 2023 ASCII zips over HTTP range requests (avoids the full ~1 GB download).
usage: python 03_lidar_tiles.py list dsm|dtm   |   python 03_lidar_tiles.py get dsm|dtm <member> [...]"""
import io, sys, os, urllib.request
import zipfile_deflate64 as zipfile  # archive uses Deflate64 (method 9)
URL={"dsm":"https://datigis.comune.fi.it/grid/MDS_LIDAR_2023_ASCII.zip","dtm":"https://datigis.comune.fi.it/grid/MDT_LIDAR_2023_ASCII.zip"}
class HttpFile(io.RawIOBase):
    def __init__(s,u):
        s.u=u; s.pos=0; s.size=int(urllib.request.urlopen(urllib.request.Request(u,method="HEAD"),timeout=60).headers["Content-Length"])
    def seekable(s): return True
    def readable(s): return True
    def tell(s): return s.pos
    def seek(s,o,w=0):
        s.pos={0:o,1:s.pos+o,2:s.size+o}[w]; return s.pos
    def readinto(s,b):
        n=len(b)
        if n==0 or s.pos>=s.size: return 0
        end=min(s.pos+n,s.size)-1
        d=urllib.request.urlopen(urllib.request.Request(s.u,headers={"Range":f"bytes={s.pos}-{end}"}),timeout=600).read()
        b[:len(d)]=d; s.pos+=len(d); return len(d)
cmd,kind=sys.argv[1],sys.argv[2]
z=zipfile.ZipFile(io.BufferedReader(HttpFile(URL[kind]),buffer_size=1<<20))
if cmd=="list":
    for i in z.infolist(): print(i.filename,i.file_size,i.compress_size)
else:
    out=os.environ.get("LIDAR_RAW",os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","_dev","data","raw","lidar2023",kind)); os.makedirs(out,exist_ok=True)
    for m in sys.argv[3:]:
        with z.open(m) as src, open(os.path.join(out,os.path.basename(m)),"wb") as dst:
            while True:
                b=src.read(1<<22)
                if not b: break
                dst.write(b)
        print("ok",m)
