"""Conservative 2-D A* for a static warehouse collision map; no sensor claims."""
import heapq
import math


class WarehousePlanner:
    def __init__(self, data, clearance=1.7, resolution=0.2):
        self.data = data
        self.clearance = clearance
        self.resolution = resolution
        self.lo = data['floor_min']
        self.hi = data['floor_max']
        self.rectangles = [(o['min'][0]-clearance, o['min'][1]-clearance,
                            o['max'][0]+clearance, o['max'][1]+clearance)
                           for o in data['obstacles']]
        self.blocked = set()
        for x0,y0,x1,y1 in self.rectangles:
            for i in range(max(0,math.floor((x0-self.lo[0])/resolution)),
                           min(math.ceil((self.hi[0]-self.lo[0])/resolution),math.ceil((x1-self.lo[0])/resolution))+1):
                for j in range(max(0,math.floor((y0-self.lo[1])/resolution)),
                               min(math.ceil((self.hi[1]-self.lo[1])/resolution),math.ceil((y1-self.lo[1])/resolution))+1):
                    self.blocked.add((i,j))

    def free(self, point):
        x,y=point
        return (all(self.lo[i]+self.clearance < v < self.hi[i]-self.clearance for i,v in enumerate(point))
                and not any(a <= x <= c and b <= y <= d for a,b,c,d in self.rectangles))

    def segment_free(self, start, end):
        if not self.free(start) or not self.free(end):
            return False
        # Exact segment/rectangle intersection prevents corner cutting.
        for a,b,c,d in self.rectangles:
            lower,upper=0.,1.
            for origin,delta,lo,hi in ((start[0],end[0]-start[0],a,c),(start[1],end[1]-start[1],b,d)):
                if abs(delta)<1e-12:
                    if not lo<=origin<=hi:
                        lower,upper=1.,0.
                        break
                else:
                    t0,t1=sorted(((lo-origin)/delta,(hi-origin)/delta))
                    lower,upper=max(lower,t0),min(upper,t1)
            if lower<=upper:
                return False
        return True

    def point(self, cell):
        return tuple(self.lo[i]+cell[i]*self.resolution for i in (0,1))

    def cell(self, point):
        return tuple(round((point[i]-self.lo[i])/self.resolution) for i in (0,1))

    def plan(self, start, goal):
        start,goal=tuple(start),tuple(goal)
        if not self.free(start):
            raise ValueError('Start lacks obstacle clearance; run prepare demo while paused')
        if not self.free(goal):
            raise ValueError('Goal lacks obstacle clearance')
        if self.segment_free(start,goal):
            return [goal]
        first,last=self.cell(start),self.cell(goal)
        if first in self.blocked or last in self.blocked or not self.segment_free(start,self.point(first)) or not self.segment_free(self.point(last),goal):
            raise ValueError('Start or goal is too close to a grid obstacle')
        costs={first:0.}; parents={}; queue=[(0.,first)]; closed=set()
        while queue:
            _,node=heapq.heappop(queue)
            if node in closed:
                continue
            if node==last:
                cells=[node]
                while node!=first:
                    node=parents[node]; cells.append(node)
                raw=[start]+[self.point(c) for c in reversed(cells)]+[goal]
                result=[]; index=0
                while index<len(raw)-1:
                    nxt=len(raw)-1
                    while nxt>index+1 and not self.segment_free(raw[index],raw[nxt]):
                        nxt-=1
                    if not self.segment_free(raw[index],raw[nxt]):
                        raise ValueError('Path clearance check failed')
                    result.append(raw[nxt]); index=nxt
                return result
            closed.add(node)
            for di,dj in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                nxt=(node[0]+di,node[1]+dj)
                if nxt in self.blocked or nxt in closed:
                    continue
                p=self.point(nxt)
                if not all(self.lo[i]+self.clearance < p[i] < self.hi[i]-self.clearance for i in (0,1)):
                    continue
                if di and dj and ((node[0]+di,node[1]) in self.blocked or (node[0],node[1]+dj) in self.blocked):
                    continue
                cost=costs[node]+math.hypot(di,dj)
                if cost<costs.get(nxt,math.inf):
                    costs[nxt]=cost; parents[nxt]=node
                    heapq.heappush(queue,(cost+math.dist(nxt,last),nxt))
        raise ValueError('No route with the required robot clearance')


def scene_map(stage):
    from pxr import Usd, UsdGeom, UsdPhysics
    cache=UsdGeom.BBoxCache(Usd.TimeCode.Default(), ['default','render','proxy'])
    obstacles=[]
    for prim in Usd.PrimRange.Stage(stage, Usd.TraverseInstanceProxies()):
        if str(prim.GetPath()).startswith('/World/IsaacBot') or not prim.HasAPI(UsdPhysics.CollisionAPI):
            continue
        if prim.GetAttribute('physics:collisionEnabled').Get() is False:
            continue
        bounds=cache.ComputeWorldBound(prim).ComputeAlignedRange()
        if bounds.IsEmpty():
            continue
        lo,hi=list(bounds.GetMin()),list(bounds.GetMax())
        if hi[2]>0.08 and lo[2]<1.8:
            obstacles.append({'path':str(prim.GetPath()),'min':lo,'max':hi})
    floor=cache.ComputeWorldBound(stage.GetPrimAtPath('/World/Structure/FloorCollider_2')).ComputeAlignedRange()
    return {'floor_min':list(floor.GetMin()),'floor_max':list(floor.GetMax()),'obstacles':obstacles}
