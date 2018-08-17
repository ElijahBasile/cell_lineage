
import CompuCellSetup

from PySteppables import *
import CompuCell
import sys

from PySteppablesExamples import MitosisSteppableBase


class ConstraintInitializerSteppable(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
    def start(self):
        xcen=int(self.dim.x/2) #finding the center of the axis
        ycen=int(self.dim.y/2)
        stem_cell= self.newCell(self.STEM) 
        #allowing attributes to better be given to the cell
        self.cellField[xcen:xcen+7,ycen:ycen+7, 0] = stem_cell
        stem_cell.targetVolume=64.0
        stem_cell.lambdaVolume=5.0
        #assigning attributes to cells
        stem_cell.dict['lineage'] = [stem_cell.id]
        stem_cell.dict['div_time'] = 0
        stem_cell.dict['num_div'] = 0
        

class GrowthSteppable(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
    def step(self,mcs):
        for cell in self.cellListByType(self.STEM):
            for neighbor , commonSurfaceArea in self.getCellNeighborDataList(cell):
                if not neighbor:
                    cell.targetVolume+=1.0     
    # alternatively if you want to make growth a function of chemical concentration uncomment lines below and comment lines above        
        # field=CompuCell.getConcentrationField(self.simulator,"PUT_NAME_OF_CHEMICAL_FIELD_HERE")
        # pt=CompuCell.Point3D()
        # for cell in self.cellList:
            # pt.x=int(cell.xCOM)
            # pt.y=int(cell.yCOM)
            # pt.z=int(cell.zCOM)
            # concentrationAtCOM=field.get(pt)
            # cell.targetVolume+=0.01*concentrationAtCOM  # you can use here any fcn of concentrationAtCOM     
        
        

class MitosisSteppable(MitosisSteppableBase):
    def __init__(self,_simulator,_frequency=1):
        MitosisSteppableBase.__init__(self,_simulator, _frequency)
    
    def step(self,mcs):
        # print "INSIDE MITOSIS STEPPABLE"
        cells_to_divide=[]
        for cell in self.cellList:
            if cell.volume>128:
                
                cells_to_divide.append(cell)
                
        for cell in cells_to_divide:
            # to change mitosis mode leave one of the below lines uncommented
            self.divideCellRandomOrientation(cell)
            # self.divideCellOrientationVectorBased(cell,1,0,0)                 # this is a valid option
            # self.divideCellAlongMajorAxis(cell)                               # this is a valid option
            # self.divideCellAlongMinorAxis(cell)                               # this is a valid option
            self.mcs=mcs
            
    def updateAttributes(self):
        self.parentCell.targetVolume /= 2.0 # reducing parent target volume                 
        self.cloneParent2Child()            
        
        #adding the id to each child from its parent's id, and taking its own
        self.childCell.dict['lineage'].append(self.childCell.id)
        self.childCell.dict['div_time']=self.mcs
        self.childCell.dict['num_div']=self.parentCell.dict['num_div']+1
        # for more control of what gets copied from parent to child use cloneAttributes function
        # self.cloneAttributes(sourceCell=self.parentCell, targetCell=self.childCell, no_clone_key_dict_list = [attrib1, attrib2] )        

from PlayerPython import *
from math import *

class colorcells(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency) 
        self.scalarCLField = self.createScalarFieldCellLevelPy("colorcells")

    def start(self):
        self.pW = self.addNewPlotWindow(_title='cell_lineage', _xAxisTitle='counter',
                                        _yAxisTitle='# of cells', _xScaleType='linear', _yScaleType='linear')
        self.pW.addPlot('lineage', _style='Dots', _color='red', _size=5)
#         self.pW.addPlot('DATA_SERIES_2', _style='Steps', _size=1)
        print "colorcells: This function is called once before simulation"
        
    def step(self,mcs):
        #don't forget about cells that are children of each other
        selection_list = self.selection_criteria(1000)
        temp_list=self.unique_ids(selection_list)
        self.pW.eraseAllData()
        
        temp_list.sort()
        counter_c=1
        num_list=[]
        for ids in temp_list:
            group=[]
            group.append(ids)
            cell_main = self.attemptFetchingCellById(ids)
            for cell in self.cellListByType(self.STEM):
                if(ids !=cell.id and ids in cell.dict['lineage']):
                    if(cell.dict['num_div'] > cell_main.dict['num_div']):
                        group.append(cell.id)
            num_list.append(len(group))
            for id_new in group:
                cell_c = self.attemptFetchingCellById(id_new)
                self.scalarCLField[cell_c] = counter_c/float(len(temp_list))
            counter_c += 1
            
        num_list.sort()    
        counter_plot = 1
        for len_grp in num_list:
            self.pW.addDataPoint("lineage", counter_plot, len_grp) 
            counter_plot+=1
#             self.pW.addDataPoint("DATA_SERIES_2", mcs, mcs)  
            
            
        
        #this is to see how short the list becomes
#         print("selection_list=",selection_list)
#         print("temp_list=",temp_list)
    def finish(self):
        # this function may be called at the end of simulation - used very infrequently though
        return
    
    def selection_criteria(self,time_interval):
        selection_list = []
        for cell in self.cellListByType(self.STEM):
            if(cell.dict['div_time'] >= time_interval):
                if(cell.id!=1):
                    selection_list.append(cell.id)
        return selection_list
            
    def unique_ids(self,selection_list):
        ele_to_delete=[]
        for cellid1 in selection_list:
            for cellid2 in selection_list:
                cell = self.attemptFetchingCellById(cellid2)
                if(cellid1!=cellid2 and cellid1 in cell.dict['lineage']):
                    if(cellid2 > cellid1 and cellid2 not in ele_to_delete):
                        ele_to_delete.append(cellid2)
                        
        temp_l = selection_list[:]
        for ids in ele_to_delete:
            temp_l.remove(ids)
        return temp_l

