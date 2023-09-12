import os
import subprocess
import json
from ffmpeg_progress_yield import FfmpegProgress
import flet as ft 

now = 0
oneOrMore = True

class SettingPanel(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.folder_file_name = [] # file name
        self.folder_file_list = [] # file absolute path

    def build(self):
        global now
        # auto
        self.auto_checkbox = ft.Checkbox(label="自動",value=False, on_change = self.set_auto)
        # bitrate
        self.bitrate_textbox = ft.TextField(label="Setting bitrate")
        # format
        self.format_dropdown = ft.Dropdown(label="格式", options=[
                                        ft.dropdown.Option("mp4"),
                                        ft.dropdown.Option("wmv"),
                                        ft.dropdown.Option("avi"),
                                        ft.dropdown.Option("mov"),
                                        ft.dropdown.Option("m4v"),
                                        ft.dropdown.Option("mkv"),
                                        ft.dropdown.Option("mp3"),
                                        ft.dropdown.Option("ogg"),
                                        ft.dropdown.Option("wav"),
                                        ft.dropdown.Option("m4a")])
        # encoder
        self.encoder_dropdown = ft.Dropdown(label="編碼",options=[
                                        ft.dropdown.Option("libx264"),
                                        ft.dropdown.Option("libx265"),
                                        ft.dropdown.Option("libaom-av1")])
        # save picker
        self.save_picker = ft.FilePicker(on_result= self.save_files)

        # file list
        self.file_list = ft.ListView(spacing=20, auto_scroll=False, height= 300)
        
        
        return ft.Column(controls=[
                # auto
                self.auto_checkbox,
                # bitrate
                self.bitrate_textbox,
                # format
                self.format_dropdown,
                # encoder
                self.encoder_dropdown,
                # save files
                ft.ElevatedButton(text="轉換", icon= ft.icons.SAVE, on_click=lambda _:self.save_picker.save_file() if oneOrMore else self.save_picker.get_directory_path()),
                self.save_picker,
                self.file_list
            ])
                
    
    def set_auto(self,e:ft.Checkbox):
        if self.auto_checkbox.value == True:
            self.bitrate_textbox.disabled = True
            self.encoder_dropdown.disabled = True
            self.format_dropdown.disabled = True
        else:
            self.bitrate_textbox.disabled = False
            self.encoder_dropdown.disabled = False
            self.format_dropdown.disabled = False
        self.update()

    def get_upload_file_path(self,e:ft.FilePickerResultEvent):
        if e.files:
            self.folder_file_name = []
            self.folder_file_list = []
            self.file_list.controls.clear()
            file = File(e.files[0].path)
            self.folder_file_name.append(e.files[0].name.split(".")[0])
            self.folder_file_list.append(e.files[0].path)
            self.file_list.controls.append(file)
            self.update()
            return e.files[0].path
        

    def get_folder_path(self,e:ft.FilePickerResultEvent):
        if e.path:
            self.folder_file_name = []
            self.folder_file_list = []
            self.file_list.controls.clear()
            for i in os.listdir(e.path):
                file_path = os.path.join(e.path, i)
                if os.path.isfile(file_path):
                    self.folder_file_name.append(i.split(".")[0])
                    self.folder_file_list.append(file_path)
                    file = File(file_path)
                    self.file_list.controls.append(file)
                    self.file_list.update()
                    #print(file_path)
                #print(self.folder_file_name)
            return e.path
        
    def convert_bitrate(self, index):
        command = fr'ffprobe -v error -select_streams v:0 -show_entries stream=bit_rate -print_format json "{self.folder_file_list[index]}"'
        data = subprocess.run(command, stdout=subprocess.PIPE).stdout
        dict = json.loads(data)
        bitrate = dict['streams'][0]['bit_rate']
        #print(bitrate)
        return bitrate
    
    def onefile(self, path):
        cmd = []
        print(path)
        if self.auto_checkbox.value == True:
            cmd = ["ffmpeg","-i", f"{self.folder_file_list[0]}", f"{path}.mp4"]
            self.cmdProgress(cmd,0)
        else:
            bitrate = self.bitrate_textbox.value if self.bitrate_textbox.value else self.convert_bitrate(0)
            file_format = self.format_dropdown.value if self.format_dropdown.value else "mp4"
            encoder = self.encoder_dropdown.value if self.encoder_dropdown.value else "libx264"
            if self.format_dropdown.value in ["mp3","ogg","wav","m4a"]:
                cmd = ["ffmpeg","-vn", "-i", f"{self.folder_file_list[0]}", f"{path}.{file_format}"]
            else:
                cmd = ["ffmpeg","-i", f"{self.folder_file_list[0]}", "-b:v", f"{bitrate}", "-c:v", f"{encoder}", f"{path}.{file_format}"]
            self.cmdProgress(cmd,0)
        
    
    def multiplefile(self, path):
        cmd = []
        print(path)
        if self.auto_checkbox.value == True:
            for index, i in enumerate(self.file_list.controls):
                cmd = ["ffmpeg", "-i", f"{self.folder_file_list[index]}", f"{os.path.join(path,self.folder_file_name[index])}_transform.mp4"]
                self.cmdProgress(cmd, index)
        else:
            for index, i in enumerate(self.file_list.controls):
                bitrate = self.bitrate_textbox.value if self.bitrate_textbox.value else self.convert_bitrate(index)
                file_format = self.format_dropdown.value if self.format_dropdown.value else "mp4"
                encoder = self.encoder_dropdown.value if self.encoder_dropdown.value else "libx264"
                if self.format_dropdown.value in ["mp3","ogg","wav","m4a"]:
                    cmd = ["ffmpeg","-vn", "-i", f"{self.folder_file_list[index]}", f"{os.path.join(path,self.folder_file_name[index])}_transform.{file_format}"]
                else:
                    cmd = ["ffmpeg","-i", f"{self.folder_file_list[index]}", "-b:v'", f"{bitrate}", "-c:v", f"{encoder}", f"{os.path.join(path,self.folder_file_name[index])}_transform.{file_format}"]
                self.cmdProgress(cmd, index)
        
    
    def cmdProgress(self, cmd, index):
        try:
            #print(cmd)
            task = FfmpegProgress(cmd)
            for progress in task.run_command_with_progress(popen_kwargs= {"creationflags": subprocess.CREATE_NO_WINDOW}):
                self.file_list.controls[index].update(progress/100)
                #print(f"{progress}/100")
        except Exception as e:
            print(e)

    
    def save_files(self, e:ft.FilePickerResultEvent):
        global now
        if e.path:
            if now == 0:
                self.onefile(e.path)
            elif now == 1:
                self.multiplefile(e.path)
            
            

class File(ft.UserControl):
    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name
        self.progress_bar = ft.ProgressBar(value=0.0)

    def build(self):
        return ft.Column(
            controls=[
                ft.Text(self.file_name),
                self.progress_bar
        ]
    )

    def update(self, value):
        self.progress_bar.value = value
        super().update()


def main(page:ft.Page):
    # main settings
    page.title = "ffmpeg-easy"
    page.window_width = 500
    page.window_center()
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    settingPanelOne = SettingPanel()
    settingPanelMultiple = SettingPanel()

    def get_upload_file_path(e:ft.FilePickerResultEvent):
        file_text.value = settingPanelOne.get_upload_file_path(e)
        page.update()
    
    def get_folder_path(e:ft.FilePickerResultEvent):
        folder_text.value = settingPanelMultiple.get_folder_path(e)
        page.update()

    def now(e):
        global now
        global oneOrMore
        now = tabs.selected_index
        if tabs.selected_index in [0]:
            oneOrMore = True    
        elif tabs.selected_index in [1]:
            oneOrMore = False
        #print(now, oneOrMore)
            
        

    # 單檔轉換
    file_text =  ft.Text()
    file_picker = ft.FilePicker(on_result= get_upload_file_path)
    file_row = ft.Container(content = ft.Row([
                # choose files 
                ft.ElevatedButton(text="選擇檔案", icon= ft.icons.UPLOAD_FILE, on_click=lambda _:file_picker.pick_files(file_type=ft.FilePickerFileType.VIDEO, allow_multiple=False)),
                file_text,
                file_picker 
            ]),margin=10)
        

    # 批次轉換
    folder_text = ft.Text()
    folder_picker = ft.FilePicker(on_result = get_folder_path)
    folder_row = ft.Container(content = ft.Row([
            # choose folder
            ft.ElevatedButton(text="選擇資料夾", icon= ft.icons.UPLOAD_FILE, on_click=lambda _:folder_picker.get_directory_path()),
            folder_text,
            folder_picker
    ]), margin=10)


    # tabs
    tabs = ft.Tabs(selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="單檔轉換",content=ft.Column(controls = [file_row,settingPanelOne])),
            ft.Tab(text="批次轉換",content=ft.Column(controls = [folder_row,settingPanelMultiple]))
        ], expand=1,on_change=now)
    

    page.add(tabs)

ft.app(target=main)