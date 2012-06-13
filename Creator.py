'''
Created on May 15, 2012

@author: andrzej
'''
from javax.swing import JFrame
from javax.swing import JMenuBar
from javax.swing import JMenu
from javax.swing import JButton
from javax.swing import JTabbedPane
from javax.swing import JPanel
from javax.swing import JMenuItem
from javax.swing import JFileChooser
from javax.swing.table import DefaultTableModel
from javax.swing import JTextField
from javax.swing import DefaultCellEditor
from javax.swing import JComboBox
from java.awt import BorderLayout
from java.awt import GridLayout
from javax.swing import JTable
from javax.swing import JScrollPane
from javax.swing import JOptionPane
import gen,re,Solve,Grapher
users = []
apps = []
drives = []

class EmptyFieldException(Exception):
    def __init__(self,value):
        self.value=value
        
    def __str__(self):
        return self.value

def Convert(level):
    if level=='low':
        return '1'
    elif level=='medium':
        return '2'
    elif level=='high':
        return '3'
    elif level=='remote':
        return '0'
    elif level=='direct':
        return '1'

class StaticContent(object):
    sets = '''set app_params := user read gen time prior;
set user_params := profile read write security access priority;
set drive_params := read_s write_s size;\n'''
    userHeaders = ['id', 'profile', 'read', 'write', 'security', 'access', 'priority']
    userProfiles = ['1', '2']
    appsHeaders = ['user','name' ,'read B/s', 'generated B/s', 'time']
    drivesHeaders = ['id','read speed', 'write speed', 'size']
    levelNames = ['low', 'medium', 'high']
    accessTypes = ['remote', 'direct']
    param_apps='''param applications : 
          user read gen time prior:=\n'''
    param_drives='''param phys_drives :
          read_s write_s size := \n'''
    param_users='''param sys_users :
          profile read write security access priority := \n'''
    apps=[]
    drives=[]
    users=[]
    

def deb(event):
    print event.paramString

def contextChange(event):
    print event.actionCommand



class Creator(object):
    def __init__(self):
        self.initialized=0
        self.tPane = JTabbedPane(JTabbedPane.TOP,stateChanged=self.updateUserInfo)     
        #setting user panel
        self.createUserTab(self.tPane)
        #setting apps panel
        self.createAppsTab(self.tPane)
        #setting drives panel
        self.createDrivesTab(self.tPane)
        self.window = JFrame('Data saver!', defaultCloseOperation=JFrame.EXIT_ON_CLOSE, size=(300, 300),
                             JMenuBar=self.createMenus(), layout=BorderLayout())
        self.window.add(self.tPane)
        self.window.visible = 1
        self.window.pack()
        self.initialized=1
    
    def createMenus(self):
        menuBar = JMenuBar()
        fileMenu = JMenu("File")
        fileMenu.add(JMenuItem("Solve", actionPerformed=self.solveData))
        menuBar.add(fileMenu)
        return menuBar
    
    def createUserTab(self, tPane):
        usersPanel = JPanel(layout=BorderLayout())
        self.tPane.addTab("Users", usersPanel)
        self.userTable = JTable(model=DefaultTableModel([[]], StaticContent.userHeaders),
                         mouseClicked=self.mousceClick)
        self.userTable.getModel().removeRow(0) #to remove first empty row
        #self.userTable.setAutoCreateRowSorter(1)
        #setting cell editors
        column = self.userTable.getColumnModel().getColumn(0) #user column
        column.setCellEditor(DefaultCellEditor(JTextField(),editingStopped=self.userNameEdited));
        column = self.userTable.getColumnModel().getColumn(2) #read column
        column.setCellEditor(DefaultCellEditor(JTextField(editable=0)));
        column = self.userTable.getColumnModel().getColumn(3) #write column
        column.setCellEditor(DefaultCellEditor(JTextField(editable=0)));
        column = self.userTable.getColumnModel().getColumn(1) #profile column
        column.setCellEditor(DefaultCellEditor(JComboBox(StaticContent.userProfiles)));
        column = self.userTable.getColumnModel().getColumn(4) #profile column
        column.setCellEditor(DefaultCellEditor(JComboBox(StaticContent.levelNames)));
        column = self.userTable.getColumnModel().getColumn(5) #profile column
        column.setCellEditor(DefaultCellEditor(JComboBox(StaticContent.accessTypes)));
        column = self.userTable.getColumnModel().getColumn(6) #profile column
        column.setCellEditor(DefaultCellEditor(JComboBox(StaticContent.levelNames)));
        #setting event listener for editing user name
        usersPanel.add(JScrollPane(self.userTable)
                       , BorderLayout.CENTER)
        buttonPanel = JPanel(layout=GridLayout(1, 2))
        buttonPanel.add(JButton("Add user", actionPerformed=self.addData))
        buttonPanel.add(JButton("Remove user", actionPerformed=self.removeData))
        usersPanel.add(buttonPanel, BorderLayout.SOUTH)
    
    def createAppsTab(self, tPane):
        appsPanel = JPanel(layout=BorderLayout())
        tPane.addTab("Applications", appsPanel)
        self.appsTable = JTable(model=DefaultTableModel([[]], StaticContent.appsHeaders))
        self.appsTable.getModel().removeRow(0)
        #self.appsTable.setAutoCreateRowSorter(1)
        #setting cell editors
        self.userBox=JComboBox(users)
        column = self.appsTable.getColumnModel().getColumn(0) #profile column
        column.setCellEditor(DefaultCellEditor(self.userBox));
        appsPanel.add(JScrollPane(self.appsTable)
                       , BorderLayout.CENTER)
        buttonPanel = JPanel(layout=GridLayout(1, 2))
        buttonPanel.add(JButton("Add application", actionPerformed=self.addData))
        buttonPanel.add(JButton("Remove application", actionPerformed=self.removeData))
        appsPanel.add(buttonPanel, BorderLayout.SOUTH)
        
    def createDrivesTab(self, tPane):
        drivesPanel = JPanel(layout=BorderLayout())
        tPane.addTab("Drives", drivesPanel)
        self.drivesTable = JTable(model=DefaultTableModel([[]], StaticContent.drivesHeaders))
        self.drivesTable.getModel().removeRow(0)
        # self.drivesTable.setAutoCreateRowSorter(1)
        drivesPanel.add(JScrollPane(self.drivesTable)
                       , BorderLayout.CENTER)
        buttonPanel = JPanel(layout=GridLayout(1, 2))
        buttonPanel.add(JButton("Add drive", actionPerformed=self.addData))
        buttonPanel.add(JButton("Remove drive", actionPerformed=self.removeData))
        drivesPanel.add(buttonPanel, BorderLayout.SOUTH)
        
    def saveData(self, fileName):
        StaticContent.apps=[]
        StaticContent.drives=[]
        StaticContent.users=[]
        
        f = open(fileName, "w+b")
        userModel=self.userTable.getModel()
        appsModel=self.appsTable.getModel()
        drivesModel=self.drivesTable.getModel()
        user_num=1
        apps_set='set apps := '
        drives_set='set drives := '
        users_set='set users := '
        apps_table=[]
        users_table=[]
        drives_table=[]
        try:        
            #fetching users and info about them
            rows=userModel.getRowCount()
            for row in range(rows):
                user=userModel.getValueAt(row,0)
                if user is None or re.match('\w',user) is None:
                    raise EmptyFieldException('Empty user name')
                users_set+=(' '+user)
                priority=Convert(userModel.getValueAt(row,6))
                app_rows=appsModel.getRowCount()
                for app_row in range(app_rows):
                    app_user=appsModel.getValueAt(app_row,0)
                    if app_user == user:
                        name=appsModel.getValueAt(app_row,1)
                        read_sec=appsModel.getValueAt(app_row,2)
                        write_sec=appsModel.getValueAt(app_row,3)
                        time=appsModel.getValueAt(app_row,4)
                        apps_set+=(' '+name)
                        apps_table.append('%*s %-*s %-*s %-*s %-*s %-s\n' % (10,name,4,str(user_num),4,read_sec,3,write_sec,4,time,priority))
                        StaticContent.apps.append(gen.app(name,user_num,write_sec,read_sec,time,priority))
                profile=userModel.getValueAt(row,1)
                read=userModel.getValueAt(row,2)
                write=userModel.getValueAt(row,3)
                security=Convert(userModel.getValueAt(row,4))
                access=Convert(userModel.getValueAt(row,5))
                users_table.append('%*s %-*s %-*s %-*s %-*s %-*s %-s\n' % (10,user,7,profile,4,read,5,write,8,security,6,access,priority))
                StaticContent.users.append(gen.user(user,profile,read,write,security,access,priority))
                user_num+=1
            users_set+=';\n'
            apps_set+=';\n'
            rows=drivesModel.getRowCount()
            for row in range(rows):
                name=drivesModel.getValueAt(row,0)
                drives_set+=' '+name
                read_s=drivesModel.getValueAt(row,1)
                write_s=drivesModel.getValueAt(row,2)
                size=drivesModel.getValueAt(row,3)
                drives_table.append('%*s %-*s %-*s %-s\n' % (10,name,6,read_s,7,write_s,size))
                StaticContent.drives.append(gen.drive(name,read_s,write_s,size))
            drives_set+=';\n'
            f.write(apps_set)
            f.write(users_set)
            f.write(drives_set)
            f.write(StaticContent.sets)
            f.write(StaticContent.param_apps)
            for app in apps_table:
                f.write(app)
            f.write(';\n')
            f.write(StaticContent.param_users)
            for usr in users_table:
                f.write(usr)
            f.write(';\n')
            f.write(StaticContent.param_drives)
            for drv in drives_table:
                f.write(drv)
            f.write(';\n')
        except EmptyFieldException, e:
            JOptionPane.showMessageDialog(None,"One of the fields is empty - "+str(e),"Empty field\n",JOptionPane.ERROR_MESSAGE);
        #except Exception, e2:
        #    JOptionPane.showMessageDialog(None,"There was an error during writing - "+str(e2),"Error",JOptionPane.ERROR_MESSAGE);
        f.close()
        
        
    def solveData(self,event):
        fileChooser = JFileChooser()
        fileChooser.showSaveDialog(None)
        out = fileChooser.selectedFile
        self.saveData(out.toString())
        grapherData=Solve.parser(Solve.python_solver(out.toString()))
        print grapherData
        tupla=(StaticContent.apps,StaticContent.drives,StaticContent.users,grapherData)
        #tupla=([gen.app('a',1,11,11,11,0)],[gen.drive('a',11,11,121)],[],[[1.0]])
        Grapher.graph(tupla)
        
    
    def mousceClick(self, event):
        column=self.userTable.getSelectedColumn()
        if (column == 0):
            row=self.userTable.getSelectedRow()
            self.tempUserName=self.userTable.getModel().getValueAt(self.userTable.convertRowIndexToModel(row),
                                                                   self.userTable.convertColumnIndexToModel(column))
            
        
    def addData(self, event):
        if (event.actionCommand == 'Add user'):
            self.userTable.getModel().insertRow(0, ['','1','0','0','low','direct','low'])
        elif (event.actionCommand == 'Add application'):
            self.appsTable.getModel().insertRow(0, [])
        elif (event.actionCommand == 'Add drive'):
            self.drivesTable.getModel().insertRow(0, [])
    def removeData(self, event):
        if (event.actionCommand == 'Remove user'):
            column=self.userTable.getSelectedColumn()
            row=self.userTable.getSelectedRow()
            selectedUser=self.userTable.getModel().getValueAt(self.userTable.convertRowIndexToModel(row),
                                                self.userTable.convertColumnIndexToModel(column))
            self.userBox.removeItem(selectedUser)
            self.userTable.getModel().removeRow(self.userTable.convertRowIndexToModel(row))
        elif(event.actionCommand == 'Remove application'):
            row=self.appsTable.getSelectedRow()
            self.appsTable.getModel().removeRow(self.appsTable.convertRowIndexToModel(row))
        elif(event.actionCommand == 'Remove drive'):
            row=self.drivesTable.getSelectedRow()
            self.drivesTable.getModel().removeRow(self.drivesTable.convertRowIndexToModel(row))
        
    #fired when there is an user id is changed        
    def userNameEdited(self, event):
        self.userBox.removeItem(self.tempUserName)
        column=self.userTable.getSelectedColumn()
        row=self.userTable.getSelectedRow()
        newValue=self.userTable.getModel().getValueAt(self.userTable.convertRowIndexToModel(row),
                                                self.userTable.convertColumnIndexToModel(column))
        self.userBox.addItem(newValue)
    #we are refreshing the info about the user
    def updateUserInfo(self,event):
        tab=self.tPane.getSelectedIndex()
        writeMap={}
        readMap={}
        #must update user read/write info
        if self.initialized==1 and tab==0:
            rows=self.appsTable.getModel().getRowCount()
            for row in range(rows):
                user=self.appsTable.getModel().getValueAt(row,0) #we have user id - hopefully it is not empty
                read=self.appsTable.getModel().getValueAt(row,2)
                gen=self.appsTable.getModel().getValueAt(row,3)
                time=self.appsTable.getModel().getValueAt(row,4)
                if user is not None and gen is not None and read is not None and time is not None:
                    if writeMap.get(user)==None:
                        writeMap[user] = 0
                    writeMap[user]+=int(gen)*int(time)
                    if readMap.get(user)==None:
                        readMap[user] = 0
                    readMap[user]+=int(read)*int(time)
            rows=self.userTable.getModel().getRowCount()
            for row in range(rows):
                user=self.userTable.getModel().getValueAt(row,0)
                if writeMap.get(user) != None and readMap.get(user) != None:
                    self.userTable.getModel().setValueAt(str(readMap[user]),row,2)
                    self.userTable.getModel().setValueAt(str(writeMap[user]),row,3)
                else:
                    self.userTable.getModel().setValueAt('0',row,2)
                    self.userTable.getModel().setValueAt('0',row,3)
                    
if __name__ == "__main__":    
    c = Creator()
