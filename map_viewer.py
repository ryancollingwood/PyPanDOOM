# hacked apart from https://github.com/treeform/simple-fps/blob/master/Tut-Simple-FPS.py
"""
awsd - movement
space - fly up
contol - fly down
mouse - look around
"""

import sys
from os import path
import csv
from collections import namedtuple
from direct.showbase.ShowBase import ShowBase

from panda3d.core import loadPrcFileData
loadPrcFileData("", "want-directtools #t")
loadPrcFileData("", "want-tk #t")

import direct.directbase.DirectStart
from direct.gui.OnscreenText import OnscreenText
import sys

from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletWorld

from panda3d.core import *

class FPS(ShowBase):
    """
        This is a very simple FPS like -
         a building block of any game i guess
    """
    def __init__(self, level_name = "map01"):
        """ create a FPS type game """
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        
        self.level_name = level_name
        self.initCollision()
        self.loadLevel()
        self.things = list()
        self.node = None


        base.accept( "escape" , sys.exit)
        base.disableMouse()        

        csv_file = f"export/{level_name}.csv"
        print(csv_file)
        if path.exists(csv_file):
            print("loading things", csv_file)

            with open(csv_file) as infile:
                reader = csv.reader(infile)
                Data = namedtuple("Thing", next(reader))  # get names from column headers
                for data in map(Data._make, reader):
                    self.things.append(data)
                    if data.type == "1":
                        self.initPlayer(float(data.x), float(data.y))
                        print(f"spawning player at {data.x}, {data.y}")
        else:
            self.initPlayer(0, 0)

        OnscreenText(text=__doc__, style=1, fg=(1,1,1,1),
            pos=(-1.3, 0.95), align=TextNode.ALeft, scale = .05)

        self.gps_text = OnscreenText(text="", style=1, fg=(1,1,1,1),
                    pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)
    
        taskMgr.add(self.update_gps_text, 'update_gps_text')

        
    def initCollision(self):
        """ create the collision system """
        base.cTrav = CollisionTraverser()
        base.cTrav.setRespectPrevTransform(True)
        base.pusher = CollisionHandlerPusher()
        
    def loadLevel(self):
        """ load the self.level 
            must have
            <Group> *something* { 
              <Collide> { Polyset keep descend } 
            in the egg file
        """
        self.level = loader.loadModel('export/{}.egg'.format(self.level_name))
        self.level.reparentTo(render)
        self.level.setTwoSided(True)
                
    def initPlayer(self, x, y):
        """ loads the player and creates all the controls for him"""
        self.node = Player(x, y)

    def update_gps_text(self, task):
        if self.node is not None:
            self.gps_text.text = str(self.node.getPos())
        return task.cont
        
class Player(object):
    """
        Player is the main actor in the fps game
    """
    speed = 100
    FORWARD = Vec3(0,2,0)
    BACK = Vec3(0,-1,0)
    LEFT = Vec3(-1,0,0)
    RIGHT = Vec3(1,0,0)
    STOP = Vec3(0)
    UP = Vec3(0, 0, 1)
    DOWN = Vec3(0, 0, -1)

    walk = STOP
    strafe = STOP
    readyToJump = False
    use = False
    jump = 0
    
    def __init__(self, x, y):
        """ inits the player """
        self.node = None
        self.x = x
        self.y = y

        self.loadModel()
        self.setUpCamera()
        #self.createCollisions()
        self.attachControls()

        # init mouse update task
        taskMgr.add(self.mouseUpdate, 'mouse-task')
        taskMgr.add(self.moveUpdate, 'move-task')
        taskMgr.add(self.useUpdate, 'use-task')
        
    def loadModel(self):
        """ make the nodepath for player """
        self.node = NodePath('player')
        self.node.reparentTo(render)
        self.node.setPos(self.x, self.y, 50)
        self.node.setScale(1)

    def getPos(self):
        pos = self.node.getPos()
        if not pos:
            return None
        return "{x},{y},{z} | {h} | {p}".format(
            x = round(pos[0]), y = round(pos[1]), z = round(pos[2]),
            h = round(self.node.getH()), p = round(base.camera.getP())
        ) 
    
    
    def setUpCamera(self):
        """ puts camera at the players node """
        self.node.setH(180)
        self.node.setP(0)

        pl =  base.cam.node().getLens()
        pl.setFov(70)
        base.cam.node().setLens(pl)
        base.camera.reparentTo(self.node)
        
    def createCollisions(self):
        """ create a collision solid and ray for the player """
        cn = CollisionNode('player')
        cn.addSolid(CollisionSphere(0,0,0,3))
        solid = self.node.attachNewNode(cn)
        base.cTrav.addCollider(solid,base.pusher)
        base.pusher.addCollider(solid,self.node, base.drive.node())
        # init players floor collisions
        ray = CollisionRay()
        ray.setOrigin(0,0,-.2)
        ray.setDirection(0,0,-1)
        cn = CollisionNode('playerRay')
        cn.addSolid(ray)
        cn.setFromCollideMask(BitMask32.bit(0))
        cn.setIntoCollideMask(BitMask32.allOff())
        solid = self.node.attachNewNode(cn)
        self.nodeGroundHandler = CollisionHandlerQueue()
        base.cTrav.addCollider(solid, self.nodeGroundHandler)
        
    def attachControls(self):
        """ attach key events """
        base.accept( "space" , self.__setattr__,["walk", self.UP])
        base.accept( "space-up" , self.__setattr__,["walk", self.STOP])
        base.accept( "control", self.__setattr__,["walk",self.DOWN])
        base.accept( "control-up", self.__setattr__,["walk",self.STOP])

        base.accept( "s" , self.__setattr__,["walk",self.STOP] )
        base.accept( "w" , self.__setattr__,["walk",self.FORWARD])
        base.accept( "s" , self.__setattr__,["walk",self.BACK] )
        base.accept( "s-up" , self.__setattr__,["walk",self.STOP] )
        base.accept( "w-up" , self.__setattr__,["walk",self.STOP] )
        base.accept( "a" , self.__setattr__,["strafe",self.LEFT])
        base.accept( "d" , self.__setattr__,["strafe",self.RIGHT] )
        base.accept( "a-up" , self.__setattr__,["strafe",self.STOP] )
        base.accept( "d-up" , self.__setattr__,["strafe",self.STOP] )

        base.accept("e", self.__setattr__,["use", True] )
        base.accept("e-up", self.__setattr__, ["use", False])
        
    def mouseUpdate(self,task):
        """ this task updates the mouse """
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if base.win.movePointer(0, int(base.win.getXSize()/2), int(base.win.getYSize()/2)):
            self.node.setH(self.node.getH() -  (x - base.win.getXSize()/2)*0.1)
            base.camera.setP(base.camera.getP() - (y - base.win.getYSize()/2)*0.1)
        return task.cont
    
    def moveUpdate(self,task): 
        """ this task makes the player move """
        # move where the keys set it
        self.node.setFluidPos(self.node,self.walk*globalClock.getDt()*self.speed)
        self.node.setFluidPos(self.node,self.strafe*globalClock.getDt()*self.speed)
        return task.cont

    def useUpdate(self, task):
        if self.use:
            pMouse = base.mouseWatcherNode.getMouse()
            pFrom = Point3()
            pTo = Point3()
            base.camLens.extrude(pMouse, pFrom, pTo)

            # Transform to global coordinates
            pFrom = render.getRelativePoint(base.cam, pFrom)
            pTo = render.getRelativePoint(base.cam, pTo)

        return task.cont


if __name__ == "__main__":
    map_name = "e1m1"

    if len(sys.argv) > 1:
        map_name = sys.argv[1] 
    
    FPS(map_name.lower())
    base.run()
