import flet as ft
import os

path = ""
folder_path_list = []
folder_path_list_new = []

def main(page:ft.Page):
    page.title = "Rename_gui"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_center()
    page.window_width = 500

    page.snack_bar = ft.SnackBar(ft.Text())

    
    def syncScroll(e:ft.ListView):
        global folder_path_list, folder_path_list_new
        if len(folder_path_list) == len(folder_path_list_new):
            file_list_new.scroll_to(offset= e.pixels, duration= 10)

    
    file_list = ft.ListView(width=220, height=350, on_scroll=syncScroll)
    file_list_new = ft.ListView(width=220, height=350)

    def get_folder_path(e: ft.FilePickerResultEvent):
        global path
        global folder_path_list
        
        if e.path:
            path = e.path
            SnackBar(path)

            folder_path_list = []
            file_list.controls.clear()

            for i in os.listdir(e.path):
                file_path = os.path.join(e.path, i)
                if os.path.isfile(file_path):
                    folder_path_list.append(i)
                    file_list.controls.append(ft.Text(folder_path_list[-1]))
                    page.update()
    
    folder_path =  ft.FilePicker(on_result=get_folder_path)

    def UseNumber(e:ft.Checkbox):
        global folder_path_list
        global folder_path_list_new
        if numberCheckBox.value == True:
            if len(folder_path_list) >= 1:
                folder_path_list_new = []
                file_list_new.controls.clear()
                for i in range(len(folder_path_list)):
                    newFIleName = ""
                    newFIleName = f"{str(i+1)}.{folder_path_list[i].split('.')[-1]}"
                    folder_path_list_new.append(newFIleName)
                    file_list_new.controls.append(ft.Text(folder_path_list_new[-1]))
                    page.update()
            else:
                SnackBar("請先開啟資料夾")
    
    numberCheckBox = ft.Checkbox(label="使用數字", on_change=UseNumber)
    def show_new_name(e:ft.TextField):
        global folder_path_list
        global folder_path_list_new
        if len(folder_path_list) >= 1:
            folder_path_list_new = []
            file_list_new.controls.clear()
            numberCheckBox.value = False
            for index, i in enumerate(folder_path_list):
                newFIleName = ""
                newFIleName = f"{e.control.value}({str(index+1)}).{folder_path_list[index].split('.')[-1]}"
                folder_path_list_new.append(newFIleName)
                file_list_new.controls.append(ft.Text(folder_path_list_new[-1]))
                page.update()
        else:
            SnackBar("請先開啟資料夾")

    def rename(e:ft.ElevatedButton):
        if (change_textfield.value!="" and len(folder_path_list_new)>=1) or (numberCheckBox.value==True and len(folder_path_list_new)>=1):
            os.chdir(path)
            for index, file in enumerate(os.listdir(path)):
                os.rename(file,folder_path_list_new[index])
            SnackBar("Done")
        else:
            SnackBar("未設定完成，請輸入新名稱之後按Enter或勾選「使用數字」")

    def SnackBar(text):
        page.snack_bar.content = ft.Text(text)
        page.snack_bar.open = True
        page.update()
            

    change_textfield = ft.TextField(on_submit=show_new_name, label="輸入新名稱(輸入完之後按Enter)")

    # hide all dialogs in overlay
    page.overlay.extend([folder_path])


    page.add(
        ft.Column(
        [ft.ElevatedButton("選擇資料夾", icon=ft.icons.FOLDER_OPEN,
                    on_click=lambda _: folder_path.get_directory_path()),

        ft.Row([
            file_list, file_list_new
        ]),
        change_textfield,
        numberCheckBox,
        ft.ElevatedButton("重命名", icon=ft.icons.DRIVE_FILE_RENAME_OUTLINE, on_click=rename)
        ], expand= True
        )
    )

ft.app(target=main)