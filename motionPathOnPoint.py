"""
Author: Prem Kumar Mahato
LinkedIn: www.linkedin.com/in/premkumarmahato
ArtStation: https://www.artstation.com/premkumarmahato8
Last Updated: 17/05/2025
Version: 1.0

About: MotionPath On Point
"""

import maya.cmds as cmds
import maya.mel as mel


class motionPath():
    """ Creating UI. """
    def __init__(self):
        self.window = "motionPath"
        self.title = "motionPath"
        self.size = [300, 300]

        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)

        self.wind = cmds.window(self.window, title = self.title)
        self.column = cmds.columnLayout(adjustableColumn = True, w=self.size[0], h=self.size[1])

        self.formLayout = cmds.formLayout(h=self.size[1])
        self.pathSelectionField = cmds.textField(h = 25, placeholderText = "*Select curve path >>>", ed=0)
        self.pathSelectButton = cmds.button("Select Path", h=25, w=100, c=self.selectPath)
        self.upObjectSelectionField = cmds.textField(h = 25, placeholderText = "*Select upVector Object >>>", ed=0)
        self.upObjectSelectionButton  = cmds.button("Select upObject", h=25, w=100, c=self.selectUpObject)
        self.objectSelectionField = cmds.scrollField('objectListField', editable=False, wordWrap=False, height=100)

        self.text = cmds.text("Author: Prem Kumar Mahato")

        self.runButton = cmds.button("Create MotionPath", c=self.run)

        cmds.formLayout(
            self.formLayout, e=1, attachForm=
            [(self.text,"top",5), (self.text,"left",5), (self.text,"right",5),
            (self.pathSelectionField,"top",25), (self.pathSelectionField,"left",5),
            (self.pathSelectButton,"top",25), (self.pathSelectButton,"right",5),
            (self.upObjectSelectionField, "top", 60), (self.upObjectSelectionField, "left", 5),
            (self.upObjectSelectionButton, "top", 60), (self.upObjectSelectionButton, "right", 5),
            (self.objectSelectionField,"top",105), (self.objectSelectionField,"left",5), (self.objectSelectionField,"right",5),
            (self.runButton,"left",5), (self.runButton,"right",5), (self.runButton,"bottom",10)],
            attachControl=[(self.pathSelectionField, "right", 5, self.pathSelectButton), (self.runButton, "top", 10, self.objectSelectionField), (self.upObjectSelectionField, "right", 5, self.upObjectSelectionButton)]
        )
        self.selectionJobScript()
        cmds.showWindow(self.window)

    def selectPath(self, *args):
        """ This function select nurbsCurve. """
        selected = cmds.ls(sl=1)[0] or []
        if selected:
            shape=cmds.listRelatives(selected, shapes=1)[0] or []
            if not cmds.objectType(shape) == "nurbsCurve":
                cmds.error("# selected object: {}, Expected: 'nurbsCurve'")
        else:
            cmds.error("# no nurbsCurve selected!")
        cmds.textField(self.pathSelectionField, e=True, tx=selected)

    def selectUpObject(self, *args):
        """ This function select nurbsCurve. """
        selected = cmds.ls(sl=1)[0] or []
        if selected:
            if not cmds.objectType(selected) == "transform":
                cmds.error("# no object transform selected!")
        else:
            cmds.error("# no upObject Selected transform selected!")
        cmds.textField(self.upObjectSelectionField, e=True, tx=selected)

    def run(self, *args):
        nurbsCurve = cmds.textField(self.pathSelectionField, q=True, tx=True)
        upObject = cmds.textField(self.upObjectSelectionField, q=True, tx=True)
        self.createMotion(path=nurbsCurve, upVector=upObject)

    def createMotion(self, path, upVector=""):
        """ This function creates motionPath. """
        selection = cmds.ls(sl=True)

        # Add attributes
        if not cmds.attributeQuery("________", node=path, exists=True):
            cmds.addAttr(path, ln="________", at="enum", en="----------:", k=1)
        if not cmds.attributeQuery("moveOnPath", node=path, exists=True):
            cmds.addAttr(path, ln="moveOnPath", sn="mop", at="float", k=1, min=0, max=1, dv=0)

        for i, each in enumerate(selection):
            tempLocator = cmds.spaceLocator(name=each+"_temp_loc")
            cmds.matchTransform(tempLocator, each)
            locator = cmds.spaceLocator(name=each+"_path_loc")
            disNode = cmds.createNode("distanceBetween", n=each + "_distanceBetween")
            motionPath = cmds.pathAnimation(locator, follow=True, fa="x", inverseFront=True, worldUpType="objectrotation",
                                            worldUpVector=[0, 1, 0], worldUpObject=upVector, c=path, fractionMode=True, n="motionPath_{}".format(i+1))
            attr = motionPath + ".u"
            maya.mel.eval("source channelBoxCommand; CBdeleteConnection \"%s\"" % attr)

            cmds.connectAttr(tempLocator[0] + ".worldMatrix[0]", disNode + ".inMatrix1")
            cmds.connectAttr(locator[0] + ".worldMatrix[0]", disNode + ".inMatrix2")
            locDis = cmds.getAttr(disNode + ".distance")
            curveLen = cmds.arclen(path)
            uValue = locDis / curveLen
            cmds.setAttr(attr, uValue)

            cmds.parentConstraint(locator, each, mo=1)

            cmds.delete(disNode, tempLocator)

            self.connection(path=path, minValue=uValue, motionPath=motionPath)

            print("motionPath have been created for: {}".format(each))

    def selectionJobScript(self):
        """ This Function Creates a job ID and records"""
        # Function to run when selection changes
        def on_selection_changed():
            selected = cmds.ls(selection=True)
            cmds.scrollField(self.objectSelectionField, edit=True, text="\n".join(selected))

        # Clean up any previous job if we stored the job ID
        if cmds.optionVar(exists="selectionChangedJobID"):
            old_job_id = cmds.optionVar(q="selectionChangedJobID")
            if cmds.scriptJob(exists=old_job_id):
                cmds.scriptJob(kill=old_job_id, force=True)
            cmds.optionVar(remove="selectionChangedJobID")

        # Create a new scriptJob
        selection_job_id = cmds.scriptJob(event=["SelectionChanged", on_selection_changed], protected=True)

        # Store the job ID in an optionVar so we can find and kill it later
        cmds.optionVar(iv=("selectionChangedJobID", selection_job_id))


        # Safe kill the job id
        def cleanup_job():
            if isinstance(selection_job_id, int) and cmds.scriptJob(exists=selection_job_id):
                cmds.scriptJob(kill=selection_job_id, force=True)

        # Create a UI-deleted watcher job
        cmds.scriptJob(uiDeleted=(self.window, cleanup_job), ro=True)

        return selection_job_id

    def connection(self, path, minValue, motionPath):
        """ This function creates a connection for the motionPath. """
        pma=cmds.createNode("plusMinusAverage", n="{}_minCompensateSum_rmp".format(motionPath))
        clamp = cmds.createNode("clamp", n="{}_clamp".format(motionPath))

        # set data
        cmds.setAttr("{}.maxR".format(clamp), 1)
        cmds.setAttr("{}.input1D[0]".format(pma), minValue)

        cmds.connectAttr("{}.moveOnPath".format(path), "{}.input1D[1]".format(pma))
        cmds.connectAttr("{}.output1D".format(pma), "{}.input.inputR".format(clamp))
        cmds.connectAttr("{}.output.outputR".format(clamp), "{}.uValue".format(motionPath))



