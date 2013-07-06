#/usr/bin/env jython

'''
Created on May 15, 2012

@author: andrzej&artur
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
from javax.swing import JSplitPane
from java.awt import BorderLayout
from java.awt import GridLayout
from javax.swing import JTable
from javax.swing import JScrollPane
from javax.swing import JOptionPane
import gen, re, Solve
from subprocess import Popen, PIPE
users = []
apps = []
drives = []

class EmptyFieldException(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return self.value

def Convert(level):
    if level == 'low':
        return '1'
    elif level == 'medium':
        return '2'
    elif level == 'high':
        return '3'
    elif level == 'remote':
        return '0'
    elif level == 'direct':
        return '1'

class StaticContent(object):
    sets = '''set app_params := user read gen time prior;
set user_params := profile read write security access priority;
set drive_params := read_s write_s size;\n'''
    userHeaders = ['id', 'profile', 'read', 'write', 'security', 'access', 'priority']
    userProfiles = ['1', '2']
    appsHeaders = ['user', 'name' , 'read B/s', 'generated B/s', 'time']
    drivesHeaders = ['id', 'read speed', 'write speed', 'size']
    levelNames = ['low', 'medium', 'high']
    accessTypes = ['remote', 'direct']
    param_apps = '''param applications : 
          user read gen time prior:=\n'''
    param_drives = '''param phys_drives :
          read_s write_s size := \n'''
    param_users = '''param sys_users :
          profile read write security access priority := \n'''
    apps = []
    drives = []
    users = []
    

def deb(event):
    print event.paramString

def contextChange(event):
    print event.actionCommand



class Creator(object):
    def __init__(self):
        self.initialized = 0
        self.tPane = JTabbedPane(JTabbedPane.TOP, stateChanged=self.updateUserInfo)     
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
        self.initialized = 1
    
    def createMenus(self):
        menuBar = JMenuBar()
        fileMenu = JMenu("File")
        fileMenu.add(JMenuItem("Solve", actionPerformed=self.solveData))
        fileMenu.add(JMenuItem("Generate", actionPerformed=self.randomData))
        fileMenu.add(JMenuItem("From file", actionPerformed=self.readFromFile))
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
        column.setCellEditor(DefaultCellEditor(JTextField(), editingStopped=self.userNameEdited));
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
        self.userBox = JComboBox(users)
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
        StaticContent.apps = []
        StaticContent.drives = []
        StaticContent.users = []
        
        f = open(fileName, "w+b")
        userModel = self.userTable.getModel()
        appsModel = self.appsTable.getModel()
        drivesModel = self.drivesTable.getModel()
        user_num = 1
        apps_set = 'set apps := '
        drives_set = 'set drives := '
        users_set = 'set users := '
        apps_table = []
        users_table = []
        drives_table = []
        try:        
            #fetching users and info about them
            rows = userModel.getRowCount()
            for row in range(rows):
                user = userModel.getValueAt(row, 0)
                if user is None or re.match('\w', user) is None:
                    raise EmptyFieldException('Empty user name')
                users_set += (' ' + user)
                priority = Convert(userModel.getValueAt(row, 6))
                app_rows = appsModel.getRowCount()
                for app_row in range(app_rows):
                    app_user = appsModel.getValueAt(app_row, 0)
                    if app_user == user:
                        name = appsModel.getValueAt(app_row, 1)
                        read_sec = appsModel.getValueAt(app_row, 2)
                        write_sec = appsModel.getValueAt(app_row, 3)
                        time = appsModel.getValueAt(app_row, 4)
                        apps_set += (' ' + name)
                        apps_table.append('%*s %-*s %-*s %-*s %-*s %-s\n' % (10, name, 4, str(user_num), 4, read_sec, 3, write_sec, 4, time, priority))
                        StaticContent.apps.append(gen.app(name, user_num, write_sec, read_sec, time, priority))
                profile = userModel.getValueAt(row, 1)
                read = userModel.getValueAt(row, 2)
                write = userModel.getValueAt(row, 3)
                security = Convert(userModel.getValueAt(row, 4))
                access = Convert(userModel.getValueAt(row, 5))
                users_table.append('%*s %-*s %-*s %-*s %-*s %-*s %-s\n' % (10, user, 7, profile, 4, read, 5, write, 8, security, 6, access, priority))
                StaticContent.users.append(gen.user(user, profile, read, write, security, access, priority))
                user_num += 1
            users_set += ';\n'
            apps_set += ';\n'
            rows = drivesModel.getRowCount()
            for row in range(rows):
                name = drivesModel.getValueAt(row, 0)
                drives_set += ' ' + name
                read_s = drivesModel.getValueAt(row, 1)
                write_s = drivesModel.getValueAt(row, 2)
                size = drivesModel.getValueAt(row, 3)
                drives_table.append('%*s %-*s %-*s %-s\n' % (10, name, 6, read_s, 7, write_s, size))
                StaticContent.drives.append(gen.drive(name, read_s, write_s, size))
            drives_set += ';\n'
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
            JOptionPane.showMessageDialog(None, "One of the fields is empty - " + str(e), "Empty field\n", JOptionPane.ERROR_MESSAGE);
        #except Exception, e2:
        #    JOptionPane.showMessageDialog(None,"There was an error during writing - "+str(e2),"Error",JOptionPane.ERROR_MESSAGE);
        f.close()
        
        
    def solveData(self, event):
        self.graphFlag=1
        fileChooser = JFileChooser()
        fileChooser.showSaveDialog(None)
        out = fileChooser.selectedFile
        if out != None:
            self.saveData(out.toString())
            #grapherData = Solve.parser(Solve.python_solver(out.toString()))
            grapherData = Solve.parser(Solve.python_solver(out.toString()))
            #print grapherData
            #creating temporary file for usual Python script
            apps = StaticContent.apps
            drives = StaticContent.drives
            users = StaticContent.users
            #apps = [gen.app('z', 1, 11, 20, 20, 5),gen.app('z2', 1, 11, 15, 15, 4)]
            #drives = [gen.drive('a', 100, 100, 100),gen.drive('b',60,60,60)]
            #grapherData=[[1.0]]
            i = 0
            for drive in drives:
                mult = drive.size
                j = 0
                for app in apps:
                    grapherData[i][j] *= float(mult)
                    j += 1
                i += 1
            self.grapherWindow(grapherData, (apps,drives,users))
        
    def randomData(self, event):
        self.graphFlag=0
        apps, drives, users = gen.generuj(20, 10, 10);
        grapherData = Solve.parser(Solve.python_solver("./wynik.dat"))
        #print grapherData
        #creating temporary file for usual Python script
        #apps = [gen.app('z', 1, 11, 20, 20, 5),gen.app('z2', 1, 11, 15, 15, 4)]
        #drives = [gen.drive('a', 100, 100, 100),gen.drive('b',60,60,60)]
        #grapherData=[[1.0]]
        i = 0
        for drive in drives:
            mult = drives[i].size
            j = 0
            for app in apps:
                grapherData[i][j] *= float(mult)
                j += 1
            i += 1
        #created graph-ready array of data, writing to temporary file
        f = open("plotData", "w")
        #grapherData=[[2.0,3.5],[1.0,3.0]]
        i_range = len(grapherData)
        j_range = len(grapherData[0])
        for i in range(i_range):
            for j in range(j_range):
                    f.write(str(float(i)) + ' ' + str(float(j)) + ' ' + str(grapherData[i][j]) + '\n')
                    f.write(str(float(i)) + ' ' + str(float(j + 1)) + ' ' + str(grapherData[i][j]) + '\n')
            f.write('\n')
            for j in range(j_range):
                    f.write(str(float(i + 1)) + ' ' + str(float(j)) + ' ' + str(grapherData[i][j]) + '\n')
                    f.write(str(float(i + 1)) + ' ' + str(float(j + 1)) + ' ' + str(grapherData[i][j]) + '\n')
            f.write('\n')
        self.grapherWindow(grapherData, (apps, drives, users))
        #f.close()
        #out = Popen(['gnuplot', '-persist', 'gnuplot_script'], stdout=PIPE).communicate()
        
    def readFromFile(self, event):
        self.graphFlag=1
        fileChooser = JFileChooser()
        fileChooser.showSaveDialog(None)
        out = fileChooser.selectedFile
        apps, drives, users = gen.readFile(out.toString())
        grapherData = Solve.parser(Solve.python_solver(out.toString()))
        #apps = [gen.app('z', 1, 11, 20, 20, 5),gen.app('z2', 1, 11, 15, 15, 4)]
        #drives = [gen.drive('a', 100, 100, 100),gen.drive('b',60,60,60)]
        #grapherData=[[1.0]]
        i = 0
        for drive in drives:
            mult = drive.size
            j = 0
            for app in apps:
                grapherData[i][j] *= float(mult)
                j += 1
            i += 1
        #created graph-ready array of data, writing to temporary file
        self.grapherWindow(grapherData, (apps,drives,users))
    def readDisk2d(self, event):
        id_dysk = 0
        
        fileChooser = JFileChooser()
        fileChooser.showSaveDialog(None)
        out = fileChooser.selectedFile
        apps, drives, users = gen.readFile(out.toString())
        grapherData = Solve.parser(Solve.python_solver(out.toString()))
        #apps = [gen.app('z', 1, 11, 20, 20, 5),gen.app('z2', 1, 11, 15, 15, 4)]
        #drives = [gen.drive('a', 100, 100, 100),gen.drive('b',60,60,60)]
        #grapherData=[[1.0]]
        i = 0
        for drive in drives:
            mult = drives[i].size
            j = 0
            for app in apps:
                grapherData[i][j] *= float(mult)
                j += 1
            i += 1
        #created graph-ready array of data, writing to temporary file
        f = open("plotData", "w")
        #grapherData=[[2.0,3.5],[1.0,3.0]]
        i_range = len(grapherData)
        j_range = len(grapherData[0])
        for j in range(j_range):
            f.write(str(float(j)) + ' ' + str(float(grapherData[id_dysk][j])) + '\n')
        f.close()
        out = Popen(['gnuplot', '-persist', 'gnuplot_script2d'], stdout=PIPE).communicate()
    
    def mousceClick(self, event):
        column = self.userTable.getSelectedColumn()
        if (column == 0):
            row = self.userTable.getSelectedRow()
            self.tempUserName = self.userTable.getModel().getValueAt(self.userTable.convertRowIndexToModel(row),
                                                                   self.userTable.convertColumnIndexToModel(column))
        
    def addData(self, event):
        if (event.actionCommand == 'Add user'):
            self.userTable.getModel().insertRow(0, ['', '1', '0', '0', 'low', 'direct', 'low'])
        elif (event.actionCommand == 'Add application'):
            self.appsTable.getModel().insertRow(0, [])
        elif (event.actionCommand == 'Add drive'):
            self.drivesTable.getModel().insertRow(0, [])
    def removeData(self, event):
        if (event.actionCommand == 'Remove user'):
            column = self.userTable.getSelectedColumn()
            row = self.userTable.getSelectedRow()
            selectedUser = self.userTable.getModel().getValueAt(self.userTable.convertRowIndexToModel(row),
                                                self.userTable.convertColumnIndexToModel(column))
            self.userBox.removeItem(selectedUser)
            self.userTable.getModel().removeRow(self.userTable.convertRowIndexToModel(row))
        elif(event.actionCommand == 'Remove application'):
            row = self.appsTable.getSelectedRow()
            self.appsTable.getModel().removeRow(self.appsTable.convertRowIndexToModel(row))
        elif(event.actionCommand == 'Remove drive'):
            row = self.drivesTable.getSelectedRow()
            self.drivesTable.getModel().removeRow(self.drivesTable.convertRowIndexToModel(row))
        
    #fired when there is an user id is changed        
    def userNameEdited(self, event):
        self.userBox.removeItem(self.tempUserName)
        column = self.userTable.getSelectedColumn()
        row = self.userTable.getSelectedRow()
        newValue = self.userTable.getModel().getValueAt(self.userTable.convertRowIndexToModel(row),
                                                self.userTable.convertColumnIndexToModel(column))
        self.userBox.addItem(newValue)
    #we are refreshing the info about the user
    def updateUserInfo(self, event):
        tab = self.tPane.getSelectedIndex()
        writeMap = {}
        readMap = {}
        #must update user read/write info
        if self.initialized == 1 and tab == 0:
            rows = self.appsTable.getModel().getRowCount()
            for row in range(rows):
                user = self.appsTable.getModel().getValueAt(row, 0) #we have user id - hopefully it is not empty
                read = self.appsTable.getModel().getValueAt(row, 2)
                gen = self.appsTable.getModel().getValueAt(row, 3)
                time = self.appsTable.getModel().getValueAt(row, 4)
                if user is not None and gen is not None and read is not None and time is not None:
                    if writeMap.get(user) == None:
                        writeMap[user] = 0
                    writeMap[user] += int(gen) * int(time)
                    if readMap.get(user) == None:
                        readMap[user] = 0
                    readMap[user] += int(read) * int(time)
            rows = self.userTable.getModel().getRowCount()
            for row in range(rows):
                user = self.userTable.getModel().getValueAt(row, 0)
                if writeMap.get(user) != None and readMap.get(user) != None:
                    self.userTable.getModel().setValueAt(str(readMap[user]), row, 2)
                    self.userTable.getModel().setValueAt(str(writeMap[user]), row, 3)
                else:
                    self.userTable.getModel().setValueAt('0', row, 2)
                    self.userTable.getModel().setValueAt('0', row, 3)
    
    #show simple window, in which user can choose which disk/application graph he or she or it wants to see
    #apps, drives, users
    def grapherWindow(self, data, tupla):
        self.__grapherWindow = JFrame('Grapher', defaultCloseOperation=JFrame.DISPOSE_ON_CLOSE, size=(300, 300)
                             , layout=GridLayout(2, 1))
        optionList = []
        i = 1
        for disk in tupla[1]:
            optionList.append("disk: " + disk.ind)
            i += 1
        i = 1
        for app in tupla[0]:
            optionList.append("application: " + app.ind)
            i += 1
        optionList.append("overall")
        self.data=data
        self.tupla=tupla
        self.grapherButton = JButton("generate graph",actionPerformed=self.generateGraphAction)
        self.iterationButton= JButton("next iteration",actionPerformed=self.nextIterationAction)
        splitPane = JSplitPane(JSplitPane.HORIZONTAL_SPLIT,
                           self.grapherButton, self.iterationButton);
        splitPane.setDividerSize(0)
        splitPane.setResizeWeight(0.5)
        self.grapherBox = JComboBox(optionList)
        self.__grapherWindow.add(self.grapherBox)
        self.__grapherWindow.add(splitPane)
        self.__grapherWindow.visible = 1
        self.__grapherWindow.pack()
       
    def generateGraphAction(self,event):
        opt=self.grapherBox.getSelectedItem()
        #index of the searched element in the data array
        i=0
        if re.match("disk: .*",opt) is not None:
            opt=opt[6:]
            for drive in self.tupla[1]:
                if opt==drive.ind:
                    break
                i+=1
            f = open("plotData", "w")
            #index of the application
            j=1
            for app in self.data[i]:
                f.write(str(j)+' '+str(app)+'\n')
                j+=1
            f.close()
            Popen(['gnuplot', '-persist', 'gnuplot_script2d_drive'], stdout=PIPE).communicate()
        elif re.match("application:.*",opt):
            opt=opt[13:]
            for app in self.tupla[0]:
                if opt==app.ind:
                    break
                i+=1
            print i
            f = open("plotData", "w")
            #index of the application
            j=1
            for drive in self.data:
                f.write(str(j)+' '+str(drive[i])+'\n')
                j+=1
            f.close()
            Popen(['gnuplot', '-persist', 'gnuplot_script2d_app'], stdout=PIPE).communicate()
        else:
            i_range = len(self.data)
            j_range = len(self.data[0])
            f = open("plotData", "w")
            for i in range(i_range):
                for j in range(j_range):
                    f.write(str(float(i)) + ' ' + str(float(j)) + ' ' + str(self.data[i][j]) + '\n')
                    f.write(str(float(i)) + ' ' + str(float(j + 1)) + ' ' + str(self.data[i][j]) + '\n')
                f.write('\n')
                for j in range(j_range):
                    f.write(str(float(i + 1)) + ' ' + str(float(j)) + ' ' + str(self.data[i][j]) + '\n')
                    f.write(str(float(i + 1)) + ' ' + str(float(j + 1)) + ' ' + str(self.data[i][j]) + '\n')
                f.write('\n')
            f.close()
            Popen(['gnuplot', '-persist', 'gnuplot_script3d'], stdout=PIPE).communicate()
    def nextIterationAction(self,event):
        self.tupla=gen.generuj(20, 10, 10)
        self.data=Solve.parser(Solve.python_solver("./wynik.dat"))
        i = 0
        for drive in self.tupla[1]:
            mult = drive.size
            j = 0
            for app in self.tupla[0]:
                self.data[i][j] *= float(mult)
                j += 1
            i += 1
        if self.graphFlag==1:
            self.grapherBox.removeAllItems()
            for disk in self.tupla[1]:
                self.grapherBox.addItem("disk: " + disk.ind)
            for app in self.tupla[0]:
                self.grapherBox.addItem("application: " + app.ind)
            self.grapherBox.addItem("overall")
            self.graphFlag=0
if __name__ == "__main__":    
    c = Creator()
