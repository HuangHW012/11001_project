# -*- coding: utf-8 -*-
# https://pythonguides.com/python-tkinter-frame/
# https://www.geeksforgeeks.org/python-add-image-on-a-tkinter-button/

from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os, shutil

from numpy.lib.type_check import common_type

from Diagnosis.Brain.Brain_tumor import *
from Diagnosis.Skin.Skin_classification import *
from Diagnosis.Chest.Chest_classification import *
from Diagnosis.Other.Other_diagnosis import *

# 產生報表
from Outcomes.generate_table import *

# 介面設計
ws = Tk()
ws.title('Medical Diagnosis')
ws.geometry('800x450')
ws.config(bg='#f7ef38')
# 其他部分偵測判定 (當點擊才會開啟糖尿病/中風偵測)
# https://www.tutorialspoint.com/how-to-remove-the-dashed-line-from-the-tkinter-menu-ui
enabled = False
menu = Menu(ws)
choose = ["Diabetes","Stroke"]
for choose_type in choose:
    menu.add_command(label=choose_type, command=lambda n=choose_type:choose_callback(n), state=DISABLED)
ws['menu']=menu
# 存檔資料的相關訊息
brain_path = ""
chest_path = ""
skin_path = ""
diabetes_data = None
stroke_data = None
# 左下暫存影像與預測結果
brain_predict_label = Label(ws)
brain_show_img = Label(ws)
chest_predict_label = Label(ws)
chest_show_img = Label(ws)
skin_predict_label = Label(ws)
skin_show_img = Label(ws)
# 使用者是否留有影像
brain_img_flag = True
chest_img_flag = True
skin_img_flag = True
# ID紀錄
now_id = ""
# 暫存註冊用的變更資料
tmp_diabetes_data = [[]]
tmp_stroke_data = [[]]
tmp_data_flag = False
stroke_processing_data = None
# 如果不存在則建檔
def init_build():
    try:
        with open('patient_infomation.pickle', 'rb') as usr_file:
            usrs_info = pickle.load(usr_file)
    except FileNotFoundError:
        # 預測
        with open('patient_infomation.pickle', 'wb') as usr_file:
            usrs_info = {'001': {"brain": './Data/Brain/001/8 no.jpg', "chest": './Data/Chest/001/IM-0023-0001.jpeg', "skin": './Data/Skin/001/ISIC_0000336.jpg', "diabetes": [['6', '148', '72', '35', '0', '33.6', '0.627', '50']], "stroke": [['Male', '56', '1', '0', 'Yes', 'Private', 'Urban', '102.37', '35.6', 'never smoked']]},
                         '002': {"brain": './Data/Brain/002/27 no.jpg', "chest": './Data/Chest/002/IM-0059-0001.jpeg', "skin": './Data/Skin/002/ISIC_0013457.jpg', "diabetes": [['7', '83', '78', '26', '71', '29.3', '0.767', '36']], "stroke": [['Female', '78', '0', '0', 'Yes', 'Self-employed', 'Rural', '109.47', '30.8', 'never smoked']]},
                         '003': {"brain": './Data/Brain/003/Y17.jpg', "chest": './Data/Chest/003/person1_bacteria_2.jpeg', "skin": './Data/Skin/003/ISIC_0013764.jpg', "diabetes": [['4', '134', '72', '0', '0', '23.8', '0.227', '60']], "stroke": [['Female', '81', '1', '1', 'Yes', 'Self-employed', 'Urban', '59.11', '20.7', 'formerly smoked']]},
                         '004': {"brain": './Data/Brain/004/Y58.JPG', "chest": './Data/Chest/004/person31_virus_70.jpeg', "skin": './Data/Skin/004/ISIC_0013891.jpg', "diabetes": [['1', '143', '74', '22', '61', '26.2', '0.256', '21']], "stroke": [['Male', '23', '0', '0', 'No', 'Private', 'Urban', '86.7', '24.6', 'Unknown']]},
                         '005': {"brain": './Data/Brain/005/no 95.jpg', "chest": './Data/Chest/005/person138_bacteria_657.jpeg', "skin": './Data/Skin/005/ISIC_0014181.jpg', "diabetes": [['0', '151', '90', '46', '0', '42.1', '0.371', '21']], "stroke": [['Male', '49', '0', '0', 'No', 'Private', 'Rural', '104.86', '31.9', 'smokes']]}
                        }
            pickle.dump(usrs_info, usr_file)
            # 必須先關閉，否則pickle.load()會出現EOFError: Ran out of input
            usr_file.close() 
    
    # 誤刪判斷，確認資料夾是否存在
    data_folder_path = './Data'
    # 影像全部沒有
    if os.path.exists(data_folder_path) == False:
        os.mkdir(data_folder_path)
        for image_type in ['Brain', 'Chest', 'Skin']:
            path = f'./Data/{image_type}'
            os.makedirs(path)
        # pickle相對應清除
        for i in usrs_info:
            print(i)
            usrs_info[i][image_type.lower()] = ""
    # 存在，但可能部分被誤刪
    else:
        for image_type in ['Brain', 'Chest', 'Skin']:
            path = f'./Data/{image_type}'
            folder = os.path.exists(path)
            # 不存在該類別
            if not folder:
                os.makedirs(path)
                for i in usrs_info:
                    usrs_info[i][image_type.lower()] = ""
            # 存在該類別，但可能病患資料夾被誤刪
            else:
                for i in usrs_info:
                    folder = os.path.exists(f'./Data/{image_type}/{i}')
                    if not folder or not os.listdir(f'./Data/{image_type}/{i}'):
                        usrs_info[i][image_type.lower()] = ""


    #print(usrs_info)
    pickle.dump(usrs_info, open("patient_infomation.pickle", "wb"))
    return usrs_info

# 登入
def usr_load():
    global brain_img_flag, chest_img_flag, skin_img_flag
    usr_name = log_em.get()
    usrs_info = init_build()
    
    #print(usrs_info)
    global enabled
    if usr_name == "":
        messagebox.showinfo(title='Warning!', message = '請輸入ID')

        enabled = False
        menu.entryconfigure(1, state=DISABLED)
        menu.entryconfigure(2, state=DISABLED)
    else:
        # 如果使用者名稱存在，則登入成功
        global brain_path, chest_path, skin_path, diabetes_data, stroke_data, now_id
        if usr_name in usrs_info:
            now_id = usr_name

            messagebox.showinfo(title='Welcome', message = f'您好, Patient ID: {usr_name}')
            brain_path = usrs_info[usr_name]['brain']
            chest_path = usrs_info[usr_name]['chest']
            skin_path = usrs_info[usr_name]['skin']
            diabetes_data = usrs_info[usr_name]['diabetes']
            stroke_data = usrs_info[usr_name]['stroke']
            
            # # 判斷是否存在影像
            if brain_path == "":
                brain_img_flag = False
            else:
                brain_img_flag = True
            if chest_path == "":
                chest_img_flag = False
            else:
                chest_img_flag = True
            if skin_path == "":
                skin_img_flag = False
            else:
                skin_img_flag = True
            # 其他
            enabled = True
            menu.entryconfigure(1, state=NORMAL)
            menu.entryconfigure(2, state=NORMAL)   
        # 如果發現使用者名稱不存在
        else:  
            is_sign_up = messagebox.askyesno('Warning!', f'Patient ID: {usr_name} 尚未註冊，請問需要先註冊?')
            # 提示需不需要註冊新使用者
            if is_sign_up:
                usr_sign_up()

# 註冊與更新
def usr_sign_up():
    global tmp_data_flag
    tmp_data_flag = True
    # 保存照片
    def save_image(patient_id, image_path):
        for i, image_type in enumerate(['Brain', 'Chest', 'Skin']):
            path = f'./Data/{image_type}/{patient_id}'
            folder = os.path.exists(path)
            if not folder:
                os.makedirs(path)
            else:
            # https://blog.csdn.net/qysh123/article/details/51923606
                shutil.rmtree(path)
                os.mkdir(path)
            # 儲存照片
            image = Image.open(image_path[i])
            image_name = image_path[i].split('/')[-1]
            image.save(f'{path}/{image_name}')
    # 獲取檔案路徑
    def input_image_path(img_type):
        file_path = filedialog.askopenfilename()
        if img_type == 'Brain':
            new_Brain.set(file_path)
        elif img_type == 'Chest':
            new_Chest.set(file_path)
        elif img_type == 'Skin':
            new_Skin.set(file_path)
        # 顯示選取的圖片
        load = Image.open(file_path) 
        new_load = load.resize((300, 300))
        render= ImageTk.PhotoImage(new_load)
        show_img = Label(window_sign_up, image = render)
        show_img.image = render
        show_img.place(x=420,y=10)
        Label(window_sign_up, text=file_path, font=('Times', 12)).place(x=380, y=320)
    # 確認Patient ID是否已經存在
    def check_id(id_number):
        with open('patient_infomation.pickle', 'rb') as usr_file:
            exist_usr_info = pickle.load(usr_file)
            if id_number in exist_usr_info:
                messagebox.showerror('Error', f'Patient ID: {id_number} 相關資訊已經紀錄!')
                # 詢問是否要更新資料
                ask_flag = messagebox.askyesnocancel('Warning', f'請問要執行覆蓋 Patient ID: {id_number} 已有資訊?')
                if ask_flag == True:
                    with open('patient_infomation.pickle', 'rb') as usr_file:
                        usrs_info = pickle.load(usr_file)
                        global diabetes_data, stroke_data
                        diabetes_data = usrs_info[id_number]['diabetes']
                        stroke_data = usrs_info[id_number]['stroke']
                else:
                    messagebox.showinfo('Warning', f'Patient ID: {id_number} 維持歷史資訊!')
            else:
                messagebox.showerror('Error', f'Patient ID: {id_number} 尚未註冊!')
            usr_file.close()
    # 註冊
    def check_information():
        global tmp_diabetes_data, tmp_stroke_data
        # 獲取註冊資訊
        name_Patient = new_name.get()
        path_brain_image = new_Brain.get()
        path_chest_image = new_Chest.get()
        path_skin_image = new_Skin.get()

        input_flag = True
        if name_Patient == "":
             messagebox.showerror('Error', 'Patient ID未輸入')
             input_flag = False
        if path_brain_image == "":
             messagebox.showerror('Error', 'Brain Image 未輸入') 
             input_flag = False   
        if path_chest_image == "":
            messagebox.showerror('Error', 'Chest Image 未輸入')
            input_flag = False
        if path_skin_image == "":
            messagebox.showerror('Error', 'Skin Image 未輸入')
            input_flag = False
        if np.array(tmp_diabetes_data == [[]]).any() == True:
            messagebox.showerror('Error', 'Diabetes Data 未輸入')
            input_flag = False
        if np.array(tmp_stroke_data == [[]]).any() == True:
            messagebox.showerror('Error', 'Stroke Data 未輸入')
            input_flag = False
        # 只有全輸入才會更新檔案
        if input_flag == True:
            global tmp_data_flag
            tmp_data_flag = False
                
            # 這裡是開啟記錄檔案，讀出註冊資訊
            with open('patient_infomation.pickle', 'rb') as usr_file:
                exist_usr_info = pickle.load(usr_file)
            # # 如果使用者名稱已經在我們的資料檔案中，則提示Error, The user has already signed up!
                if name_Patient in exist_usr_info:
                    messagebox.showerror('Error', f'Patient ID: {name_Patient} 相關資訊已經紀錄!')
                    ask_flag = messagebox.askyesnocancel('Warning', f'請問要覆蓋 Patient ID: {name_Patient} 已有資訊?')
                    if ask_flag == True:
                        exist_usr_info[name_Patient] = {"brain": path_brain_image, "chest": path_chest_image, "skin": path_skin_image, "diabetes": tmp_diabetes_data, "stroke": tmp_stroke_data}
                        save_image(name_Patient, [path_brain_image, path_chest_image, path_skin_image])
                        with open('patient_infomation.pickle', 'wb') as usr_file:
                            pickle.dump(exist_usr_info, usr_file)
                            messagebox.showinfo('Welcome', f'Patient ID: {name_Patient} 覆蓋資訊成功!')
                    else:
                        messagebox.showinfo('Warning', f'Patient ID: {name_Patient} 維持歷史資訊!')
                    # 銷燬視窗。
                    window_sign_up.destroy()
            # # 最後如果輸入無以上錯誤，提示註冊成功Welcome！ 然後銷燬視窗。
                else:
                    exist_usr_info[name_Patient] = {"brain": path_brain_image, "chest": path_chest_image, "skin": path_skin_image, "diabetes": tmp_diabetes_data, "stroke": tmp_stroke_data}
                    save_image(name_Patient, [path_brain_image, path_chest_image, path_skin_image])
                    with open('patient_infomation.pickle', 'wb') as usr_file:
                        pickle.dump(exist_usr_info, usr_file)
                    messagebox.showinfo('Welcome', f'Patient ID: {name_Patient} 紀錄成功!')
                    # 銷燬視窗。
                    window_sign_up.destroy()
                    usr_file.close() 
    def choose_check(n):
        if n == 'Diabetes':
            diabetes()
        elif n == 'Stroke':
            stroke()
    # 定義長在視窗上的視窗
    window_sign_up = Toplevel(ws)
    window_sign_up.geometry('780x380')
    window_sign_up.title('Register')
    # 其他部分偵測
    sign_up_menu = Menu(window_sign_up)
    choose = ["Diabetes","Stroke"]
    for choose_type in choose:
        sign_up_menu.add_command(label=choose_type, command=lambda n=choose_type:choose_check(n))
    window_sign_up['menu']=sign_up_menu

    # 輸入資訊
    new_name = StringVar()  
    new_name.set('000')  
    Label(window_sign_up, text='Patient ID: ', font=('Times', 16)).place(x=10, y=10)  
    Entry(window_sign_up, textvariable=new_name, font=('Times', 16), width = 8).place(x=130, y=10)   
    Button(window_sign_up, text='Check',  command = lambda: check_id(new_name.get())).place(x=320, y=10)

    new_Brain = StringVar()
    Label(window_sign_up, text='Brain Image: ', font=('Times', 16)).place(x=10, y=50)
    Entry(window_sign_up, textvariable=new_Brain, font=('Times', 14), width = 20).place(x=130, y=50)
    Button(window_sign_up, text='Upload',  command = lambda: input_image_path('Brain')).place(x=320, y=50)

    new_Chest = StringVar()
    Label(window_sign_up, text='Chest Image: ', font=('Times', 16)).place(x=10, y=90)
    Entry(window_sign_up, textvariable=new_Chest, font=('Times', 14), width = 20).place(x=130, y=90)
    Button(window_sign_up, text='Upload',  command = lambda: input_image_path('Chest')).place(x=320, y=90)

    new_Skin = StringVar()
    Label(window_sign_up, text='Skin Image: ', font=('Times', 16)).place(x=10, y=130)
    Entry(window_sign_up, textvariable=new_Skin, font=('Times', 14), width = 20).place(x=130, y=130)
    Button(window_sign_up, text='Upload',  command = lambda: input_image_path('Skin')).place(x=320, y=130)
    
    # 下面的 sign_to_Hongwei_Website
    btn_comfirm_sign_up = Button(window_sign_up, text='Sign up', font=('Times', 16), command=check_information)
    btn_comfirm_sign_up.place(x=150, y=180)

# 清空指定資料(for 字典)
def del_data():
    usr_name = log_em.get()
    usrs_info = init_build()
    messagebox.showinfo('Warning', f'啟動刪除資料功能!')
    #exist_usr_info = pickle.load(usrs_info)
    if usr_name in usrs_info and (usr_name not in ['001', '002', '003', '004', '005']):
        ask_flag = messagebox.askyesnocancel('Warning', f'請問要刪除 Patient ID: {usr_name} 已有資訊?')
        if ask_flag == True:
             # 清空影像資料夾
            for image_type in ['Brain', 'Chest', 'Skin']:
                path = f'./Data/{image_type}/{usr_name}'
                shutil.rmtree(path)
            # 清空patient_infomation資料
            del usrs_info[usr_name]
            # 更新檔案
            pickle.dump(usrs_info, open("patient_infomation.pickle", "wb"))
            messagebox.showinfo('Welcome', f'Patient ID: {usr_name} 刪除資訊成功!')
        else:
            messagebox.showinfo('Warning', f'Patient ID: {usr_name} 維持歷史資訊!')
    else:
        messagebox.showerror('Error', f'刪除失敗，Patient ID: {usr_name}錯誤或不存在或在不被允許刪除的範圍(000~005)!')

# 清除當前影像資料
def clear_image():
    global enabled
    ask_flag = messagebox.askyesnocancel('Warning', '請問是否要清空當前資料?')
    if ask_flag == True:
        draw_photo(None, 0, 0, 0, "", "brain", True)
        draw_photo(None, 0, 0, 0, "", "chest", True)
        draw_photo(None, 0, 0, 0, "", "skin", True)
        if enabled == True:
            enabled = False
            menu.entryconfigure(1, state=DISABLED)
            menu.entryconfigure(2, state=DISABLED)
    
# 畫圖
def draw_photo(image_path, size, x, y, diagnosis_coutcome, image_type, flag = False):
    global brain_show_img, brain_predict_label
    global chest_show_img, chest_predict_label
    global skin_show_img, skin_predict_label
    if flag == True:
        if image_type == 'brain':
            brain_show_img.config(image='')
            brain_predict_label.config(text='')
        if image_type == 'chest':
            chest_predict_label.config(text='')
            chest_show_img.config(image='')
        if image_type == 'skin':
            skin_show_img.config(image='')
            skin_predict_label.config(text='')
        diagnosis_type.set('Diagnosis outcomes')
        diagnosis_outcome.set('')
    else:
        # # 照片
        load = Image.open(image_path)
        new_load = load.resize((size, size))
        render= ImageTk.PhotoImage(new_load)
        show_img = Label(ws, image = render)
        show_img.image = render
        show_img.place(x=x,y=y)
        # 標題
        if diagnosis_coutcome in ['Tumor!', 'Pneumonia!', 'Diabetes!', 'Stroke!', 'Melanoma', 'Nevus', 'Seborrheic Keratosis']:
            predict_label = Label(ws, text=diagnosis_coutcome, font=('Times', 9), fg = '#f00')
        else:
            predict_label = Label(ws, text=diagnosis_coutcome, font=('Times', 9))
        predict_label.place(x = x+50, y = 422)

        if image_type == 'brain':
            brain_show_img = show_img
            brain_predict_label = predict_label
        elif image_type == 'chest':
            chest_show_img = show_img
            chest_predict_label = predict_label
        elif image_type == 'skin':
            skin_show_img = show_img
            skin_predict_label = predict_label
        
# 器官偵測   
def brain():
    #global brain_img_flag, chest_img_flag, skin_img_flag
    global brain_path, brain_img_flag, now_id, brain_show_img
    if brain_show_img != None:
        draw_photo(None, 0, 0, 0, "", "brain", True)
    if now_id == "":
        messagebox.showerror('Error', 'Patient ID 尚未登入')
        ask_flag = messagebox.askyesnocancel('Warning', f'請問要先單獨器官偵測?')
        if ask_flag == True:
            brain_path = filedialog.askopenfilename()
            
            diagnosis_type.set('[Brain] Diagnosis')
            brain_diagnosis = Brain_tumor(brain_path)
            diagnosis_outcome.set(brain_diagnosis.predict())
            draw_photo(brain_path, 140, 50, 280, brain_diagnosis.predict(), 'brain')
            brain_path = ""
    else:
        if brain_img_flag == True:
            diagnosis_type.set('[Brain] Diagnosis')
            brain_diagnosis = Brain_tumor(brain_path)
            diagnosis_outcome.set(brain_diagnosis.predict())
            draw_photo(brain_path, 140, 50, 280, brain_diagnosis.predict(), 'brain')
        else:
            messagebox.showerror('Error', f'Patient ID {now_id}並未有照片!')
            ask_flag = messagebox.askyesnocancel('Warning', f'請問要載入圖片並進行偵測?')
            if ask_flag == True:
                brain_path = filedialog.askopenfilename()
                
                diagnosis_type.set('[Brain] Diagnosis')
                brain_diagnosis = Brain_tumor(brain_path)
                diagnosis_outcome.set(brain_diagnosis.predict())

                # 若無建立資料夾要先建立
                path = f'./Data/Brain/{now_id}'
                folder = os.path.exists(path)
                # 不存在該類別
                if not folder:
                    os.makedirs(path)
                # 儲存照片
                image = Image.open(brain_path)
                image_name = brain_path.split('/')[-1]
                image.save(f'{path}/{image_name}') 
  
                draw_photo(brain_path, 140, 50, 280, brain_diagnosis.predict(), 'brain')
                # 紀錄並更新
                with open('patient_infomation.pickle', 'rb') as usr_file:
                    usrs_info = pickle.load(usr_file)
                    usrs_info[now_id]['brain'] = f'{path}/{image_name}'
                    pickle.dump(usrs_info, open("patient_infomation.pickle", "wb"))
                
                brain_img_flag = True
def chest():
    global chest_path, chest_img_flag, now_id, chest_show_img
    if chest_show_img != None:
        draw_photo(None, 0, 0, 0, "", "chest", True)
    if now_id == "":
        messagebox.showerror('Error', 'Patient ID 尚未登入')
        ask_flag = messagebox.askyesnocancel('Warning', f'請問要先單獨器官偵測?')
        if ask_flag == True:
            chest_path = filedialog.askopenfilename()

            diagnosis_type.set('[Chest] Diagnosis')
            chest_diagnosis = Chest_classification(chest_path)
            diagnosis_outcome.set(chest_diagnosis.predict())
            draw_photo(chest_path, 140, 200, 280, chest_diagnosis.predict(), 'chest')
            chest_path = ""
    else:
        messagebox.showerror('Error', f'Patient ID {now_id}並未有照片!')
        ask_flag = messagebox.askyesnocancel('Warning', f'請問要載入圖片並進行偵測?')
        if ask_flag == True:
            chest_path = filedialog.askopenfilename()
                
            diagnosis_type.set('[Chest] Diagnosis')
            chest_diagnosis = Brain_tumor(chest_path)
            diagnosis_outcome.set(chest_diagnosis.predict())

            # 若無建立資料夾要先建立
            path = f'./Data/Chest/{now_id}'
            folder = os.path.exists(path)
            # 不存在該類別
            if not folder:
                os.makedirs(path)
            # 儲存照片
            image = Image.open(chest_path)
            image_name = chest_path.split('/')[-1]
            image.save(f'{path}/{image_name}') 

            draw_photo(chest_path, 140, 200, 280, brain_diagnosis.predict(), 'chest')
            # 紀錄並更新
            with open('patient_infomation.pickle', 'rb') as usr_file:
                usrs_info = pickle.load(usr_file)
                usrs_info[now_id]['chest'] = f'{path}/{image_name}'
            pickle.dump(usrs_info, open("patient_infomation.pickle", "wb"))
            chest_img_flag = True
def skin():
    global skin_path, skin_img_flag, now_id, skin_show_img
    if skin_show_img != None:
        draw_photo(None, 0, 0, 0, "", "skin", True)
    if now_id == "":
        messagebox.showerror('Error', 'Patient ID 尚未登入')
        ask_flag = messagebox.askyesnocancel('Warning', f'請問要先單獨器官偵測?')
        if ask_flag == True:
            skin_path = filedialog.askopenfilename()

            diagnosis_type.set('[Skin] Diagnosis')
            skin_diagnosis = Skin_classification(skin_path)
            draw_photo(skin_path, 140, 350, 280, skin_diagnosis.predict(), 'skin')
            skin_path = ""
    else:
        if skin_img_flag == True:
            diagnosis_type.set('[Skin] Diagnosis')
            skin_diagnosis = Skin_classification(skin_path)
            diagnosis_outcome.set(skin_diagnosis.predict())
            draw_photo(skin_path, 140, 350, 280, skin_diagnosis.predict(), 'skin')
        else:
            messagebox.showerror('Error', f'Patient ID {now_id}並未有照片!')
            ask_flag = messagebox.askyesnocancel('Warning', f'請問要載入圖片並進行偵測?')
            if ask_flag == True:
                skin_path = filedialog.askopenfilename()
                    
                diagnosis_type.set('[Skin] Diagnosis')
                skin_diagnosis = Brain_tumor(skin_path)
                diagnosis_outcome.set(skin_diagnosis.predict())

                # 若無建立資料夾要先建立
                path = f'./Data/Skin/{now_id}'
                folder = os.path.exists(path)
                # 不存在該類別
                if not folder:
                    os.makedirs(path)
                # 儲存照片
                image = Image.open(skin_path)
                image_name = skin_path.split('/')[-1]
                image.save(f'{path}/{image_name}') 

                draw_photo(skin_path, 140, 350, 280, brain_diagnosis.predict(), 'skin')
                # 紀錄並更新
                with open('patient_infomation.pickle', 'rb') as usr_file:
                    usrs_info = pickle.load(usr_file)
                    usrs_info[now_id]['skin'] = f'{path}/{image_name}'
                    pickle.dump(usrs_info, open("patient_infomation.pickle", "wb"))
                skin_img_flag = True
# 判斷哪種其他偵測
def choose_callback(n):
    if n == 'Diabetes':
        diabetes()
    elif n == 'Stroke':
        stroke()
def body():
    global enabled
    if enabled == False:
        messagebox.showerror('Error', 'Patient ID 尚未登入')
        ask_flag = messagebox.askyesnocancel('Warning', f'請問要先單獨器官偵測?')
        if ask_flag == True:
            enabled = True
            menu.entryconfigure(1, state=NORMAL)
            menu.entryconfigure(2, state=NORMAL)    
    else:
        enabled = True
        menu.entryconfigure(1, state=NORMAL)
        menu.entryconfigure(2, state=NORMAL)   

# 糖尿病偵測
def diabetes():
    def get_informations():
        # 偵錯
        flag = True  
        if new_pregnancies.get() == "":
            messagebox.showerror('Error', '未輸入[pregnancies]')
            flag = False
        if new_glucose.get() == "":
            messagebox.showerror('Error', '未輸入[glucose]')
            flag = False
        if new_bloodPressure.get() == "":
            messagebox.showerror('Error', '未輸入[bloodPressure]')
            flag = False
        if new_skinThickness.get() == "":
            messagebox.showerror('Error', '未輸入[skinThickness]')
            flag = False
        if new_insulin.get() == "":
            messagebox.showerror('Error', '未輸入[insulin]')
            flag = False
        if new_BMI.get() == "":
            messagebox.showerror('Error', '未輸入[BMI]')
            flag = False
        if new_diabetesPedigreeFunction.get() == "":
            messagebox.showerror('Error', '未輸入[diabetesPedigreeFunction]')
            flag = False
        if new_age.get() == "":
            messagebox.showerror('Error', '未輸入[age]')
            flag = False

        if flag == True:
            type_pregnancies = float(new_pregnancies.get())
            type_glucose = float(new_glucose.get())
            type_bloodPressure = float(new_bloodPressure.get())
            type_sloodPressure = float(new_skinThickness.get())
            type_insulin = float(new_insulin.get())
            type_BMI = float(new_BMI.get())
            type_diabetesPedigreeFunction = float(new_diabetesPedigreeFunction.get())
            type_age = float(new_age.get())
            
            data = np.array([[type_pregnancies, type_glucose, type_bloodPressure, type_sloodPressure, type_insulin, type_BMI, type_diabetesPedigreeFunction, type_age]])
            
            global tmp_diabetes_data, tmp_data_flag
            if tmp_data_flag == True:
                tmp_diabetes_data = [[new_pregnancies.get(), new_glucose.get(), new_bloodPressure.get(), new_skinThickness.get(), new_insulin.get(), new_BMI.get(), new_diabetesPedigreeFunction.get(), new_age.get()]]
                window_diabetes.destroy()
            else:
                other_diagnosis = Other_diagnosis('DIABETES', data)
                diagnosis_type.set('[Diabetes] Diagnosis')
                diagnosis_outcome.set(other_diagnosis.predict())
            # 關閉視窗
            #window_diabetes.destroy()
    # 定義長在視窗上的視窗
    window_diabetes = Toplevel(ws)
    window_diabetes.geometry('300x350')
    window_diabetes.title('DIABETES')

    global diabetes_data
    new_pregnancies = StringVar() 
    
    if diabetes_data != None:
        new_pregnancies.set(diabetes_data[0][0])
    else:
        new_pregnancies.set('6') 
    Label(window_diabetes, text='Pregnancies: ').place(x=10, y=10)  
    entry_pregnancies = Entry(window_diabetes, textvariable=new_pregnancies, width=8) 
    entry_pregnancies.place(x=180, y=10)  

    new_glucose = StringVar()
    if diabetes_data != None:
        new_glucose.set(diabetes_data[0][1])
    else:
        new_glucose.set('148')
    Label(window_diabetes, text='Glucose: ').place(x=10, y=50)
    entry_glucose = Entry(window_diabetes, textvariable=new_glucose, width=8)
    entry_glucose.place(x=180, y=50)

    new_bloodPressure = StringVar()
    if diabetes_data != None:
        new_bloodPressure.set(diabetes_data[0][2])
    else:
        new_bloodPressure.set('72')
    Label(window_diabetes, text='BloodPressure: ').place(x=10, y=90)
    entry_bloodPressure = Entry(window_diabetes, textvariable=new_bloodPressure, width=8)
    entry_bloodPressure.place(x=180, y=90)

    new_skinThickness = StringVar()
    if diabetes_data != None:
        new_skinThickness.set(diabetes_data[0][3])
    else:
        new_skinThickness.set('35')
    Label(window_diabetes, text='SkinThickness: ').place(x=10, y=130)
    entry_skinThicknes = Entry(window_diabetes, textvariable=new_skinThickness, width=8)
    entry_skinThicknes.place(x=180, y=130)

    new_insulin = StringVar()
    if diabetes_data != None:
        new_insulin.set(diabetes_data[0][4])
    else:
        new_insulin.set('0')
    Label(window_diabetes, text='Insulin: ').place(x=10, y=170)
    entry_insulin = Entry(window_diabetes, textvariable=new_insulin, width=8)
    entry_insulin.place(x=180, y=170)

    new_BMI = StringVar()
    if diabetes_data != None:
        new_BMI.set(diabetes_data[0][5])
    else:
        new_BMI.set('50')
    Label(window_diabetes, text='BMI: ').place(x=10, y=210)
    entry_BMI = Entry(window_diabetes, textvariable=new_BMI, width=8)
    entry_BMI.place(x=180, y=210)    

    new_diabetesPedigreeFunction = StringVar()
    if diabetes_data != None:
        new_diabetesPedigreeFunction.set(diabetes_data[0][6])
    else:
        new_diabetesPedigreeFunction.set('0.627')
    Label(window_diabetes, text='DiabetesPedigreeFunction: ').place(x=10, y=250)
    entry_diabetesPedigreeFunction = Entry(window_diabetes, textvariable=new_diabetesPedigreeFunction, width=8)
    entry_diabetesPedigreeFunction.place(x=180, y=250)   

    new_age = StringVar()
    if diabetes_data != None:
        new_age.set(diabetes_data[0][7])
    else:
        new_age.set('50')
    Label(window_diabetes, text='Age: ').place(x=10, y=290)
    entry_age = Entry(window_diabetes, textvariable=new_age, width=8)
    entry_age.place(x=180, y=290)   

    # 下面的 sign_to_Hongwei_Website
    btn_comfirm_sign_up = Button(window_diabetes, text='Send', command=get_informations)
    btn_comfirm_sign_up.place(x=180, y=320)
# 中風偵測
def stroke():

    def get_informations():
        # 偵錯
        flag = True  
        if new_age.get() == "":
            messagebox.showerror('Error', '未輸入[gender]')
            flag = False
        if new_hypertension.get() == "":
            messagebox.showerror('Error', '未輸入[hypertension]')
            flag = False
        if new_heart_disease.get() == "":
            messagebox.showerror('Error', '未輸入[heart_disease]')
            flag = False
        if new_avg_glucose_level.get() == "":
            messagebox.showerror('Error', '未輸入[avg_glucose_level]')
            flag = False
        if new_bmi.get() == "":
            messagebox.showerror('Error', '未輸入[bmi]')
            flag = False

        if flag == True:
            type_gender_ = new_gender.get()
            type_age = float(new_age.get())
            type_hypertension = float(new_hypertension.get())
            type_heart_disease = float(new_heart_disease.get())
            type_ever_married_ = new_ever_married.get()
            type_work_type_ = new_work_type.get()
            type_Residence_type_ = new_Residence_type.get()
            type_avg_glucose_level = float(new_avg_glucose_level.get())
            type_bmi = float(new_bmi.get())
            type_smoking_status_ = new_smoking_status.get()
        

            type_gender = 1 if type_gender_ == 'Male' else 0
            type_ever_married = 1 if type_ever_married_ == 'Yes' else 0
            type_work_type = 4 if type_work_type_ == 'children' else 3 if type_work_type_ == 'Self-employed' else 2 if type_work_type_ == 'Self-Private' else 1 if type_work_type_ == 'Never_worked ' else 0
            type_Residence_type = 1 if type_Residence_type_ == 'Urban' else 0
            type_smoking_status = 3 if type_smoking_status_ == 'smokes' else 2 if type_smoking_status_ == 'never smoked' else 1 if type_smoking_status_ == 'formerly smoked' else 0

            data = np.array([[type_gender, type_age, type_hypertension, type_heart_disease, type_ever_married, type_work_type, type_Residence_type, type_avg_glucose_level, type_bmi, type_smoking_status]])
        
            global tmp_stroke_data, tmp_data_flag
            if tmp_data_flag == True:
                tmp_stroke_data =  [[new_gender.get(), new_age.get(), new_hypertension.get(), new_heart_disease.get(), new_ever_married.get(), new_work_type.get(), new_Residence_type.get(), new_avg_glucose_level.get(), new_bmi.get(), new_smoking_status.get()]]
                window_stroke.destroy()
            else:
                other_diagnosis = Other_diagnosis('STROKE', data)
                diagnosis_type.set('[Stroke] Diagnosis')
                diagnosis_outcome.set(other_diagnosis.predict())
            # 關閉視窗
            #window_stroke.destroy()
    global stroke_processing_data
    # 定義長在視窗上的視窗
    window_stroke = Toplevel(ws)
    window_stroke.geometry('300x450')
    window_stroke.title('STROKE')

    # 選單框架
    gender_options = ["Female", "Male"]
    new_gender = StringVar()
    if stroke_data != None:
        new_gender.set(stroke_data[0][0])
    else:
        new_gender.set(gender_options[1])
    Label(window_stroke, text='Gender: ').place(x=10, y=10)
    entry_gender = OptionMenu(window_stroke, new_gender, *gender_options)
    entry_gender.place(x=150, y=10)  

    new_age = StringVar() 
    if stroke_data != None:
        new_age.set(stroke_data[0][1])
    else:
        new_age.set('67') 
    Label(window_stroke, text='Age: ').place(x=10, y=50)  
    entry_age = Entry(window_stroke, textvariable=new_age, width=8) 
    entry_age.place(x=150, y=50) 

    new_hypertension = StringVar()
    if stroke_data != None:
        new_hypertension.set(stroke_data[0][2])
    else:
        new_hypertension.set('0')
    Label(window_stroke, text='Hypertension: ').place(x=10, y=90)
    entry_hypertension = Entry(window_stroke, textvariable=new_hypertension, width=8)
    entry_hypertension.place(x=150, y=90)

    new_heart_disease = StringVar()
    if stroke_data != None:
        new_heart_disease.set(stroke_data[0][3])
    else:
        new_heart_disease.set('1')
    Label(window_stroke, text='Heart_disease: ').place(x=10, y=130)
    entry_heart_disease = Entry(window_stroke, textvariable=new_heart_disease, width=8)
    entry_heart_disease.place(x=150, y=130)

    ever_married_options = ["Yes", "No"]
    new_ever_married = StringVar()
    if stroke_data != None:
        new_ever_married.set(stroke_data[0][4])
    else:
        new_ever_married.set(ever_married_options[0])
    Label(window_stroke, text='Ever_married: ').place(x=10, y=170)
    entry_ever_married = OptionMenu(window_stroke, new_ever_married, *ever_married_options)
    entry_ever_married.place(x=150, y=170)     

    work_type_options = ["children", "Self-employed", "Private", "Never_worked", "Govt_job"]
    new_work_type = StringVar()
    if stroke_data != None:
        new_work_type.set(stroke_data[0][5])
    else:
        new_work_type.set(work_type_options[2])
    Label(window_stroke, text='Work_type: ').place(x=10, y=210)
    entry_work_type = OptionMenu(window_stroke, new_work_type, *work_type_options)
    entry_work_type.place(x=150, y=210) 

    Residence_type_options = ["Urban", "Rural"]
    new_Residence_type = StringVar()
    if stroke_data != None:
        new_Residence_type.set(stroke_data[0][6])
    else:
        new_Residence_type.set(Residence_type_options[0])
    Label(window_stroke, text='Residence_type: ').place(x=10, y=250)
    entry_Residence_type = OptionMenu(window_stroke, new_Residence_type, *Residence_type_options)
    entry_Residence_type.place(x=150, y=250)    

    new_avg_glucose_level = StringVar()
    if stroke_data != None:
        new_avg_glucose_level.set(stroke_data[0][7])
    else:
        new_avg_glucose_level.set('228.69')
    Label(window_stroke, text='Avg_glucose_level: ').place(x=10, y=290)
    entry_avg_glucose_level = Entry(window_stroke, textvariable=new_avg_glucose_level, width=8)
    entry_avg_glucose_level.place(x=150, y=290)  

    new_bmi = StringVar()
    if stroke_data != None:
        new_bmi.set(stroke_data[0][8])
    else:
        new_bmi.set('36.6')
    Label(window_stroke, text='BMI: ').place(x=10, y=330)
    entry_bmi = Entry(window_stroke, textvariable=new_bmi, width=8)
    entry_bmi.place(x=150, y=330)

    smoking_status_options = ["smokes", "never smoked", "formerly smoked", "Unknown"]
    new_smoking_status = StringVar()
    if stroke_data != None:
        new_smoking_status.set(stroke_data[0][9])
    else:
        new_smoking_status.set(smoking_status_options[2])
    Label(window_stroke, text='Smoking_status: ').place(x=10, y=370)
    entry_smoking_status = OptionMenu(window_stroke, new_smoking_status, *smoking_status_options)
    entry_smoking_status.place(x=150, y=370)    

    # 下面的 sign_to_Hongwei_Website
    btn_comfirm_sign_up = Button(window_stroke, text='Send', command=get_informations)
    btn_comfirm_sign_up.place(x=150, y=420)







# 報表產生:
def output_print():
    global now_id, brain_path, chest_path, skin_path, diabetes_data, stroke_data
    if now_id == "":
        messagebox.showerror('Error', 'Patient ID 尚未登入')
    else:
        messagebox.showinfo('Wraning', f'開啟診斷報表輸出功能!')
        ask_flag = messagebox.askyesnocancel('Warning', f'請問要對Patient ID: {now_id}產生診斷報表?')
        if ask_flag == True:
            diagnosis_outcome = []
            which_outcome = []
            if brain_path != "":
                brain_diagnosis = Brain_tumor(brain_path)
                diagnosis_outcome.append(brain_diagnosis.predict())
                which_outcome.append(True)
            else:
                which_outcome.append(False)
            if chest_path != "":
                chest_diagnosis = Brain_tumor(chest_path)
                diagnosis_outcome.append(chest_diagnosis.predict())
                which_outcome.append(True)
            else:
                which_outcome.append(False)
            if skin_path != "":
                skin_diagnosis = Brain_tumor(skin_path)
                diagnosis_outcome.append(skin_diagnosis.predict())
                which_outcome.append(True)
            else:
                which_outcome.append(False)
                
            if diabetes_data != None:
                diabetes_diagnosis = Other_diagnosis('DIABETES', diabetes_data)
                diagnosis_outcome.append(diabetes_diagnosis.predict())
                which_outcome.append(True)
            else:
                which_outcome.append(False)
            if stroke_data != None:
                
                gender = 1 if stroke_data[0][0] == 'Male' else 0
                age = float(stroke_data[0][1])
                hypertension = float(stroke_data[0][2])
                heart_disease = float(stroke_data[0][3])
                ever_married = 1 if stroke_data[0][4] == 'Yes' else 0
                work_type = 4 if stroke_data[0][5] == 'children' else 3 if stroke_data[0][5] == 'Self-employed' else 2 if stroke_data[0][5] == 'Self-Private' else 1 if stroke_data[0][5] == 'Never_worked ' else 0
                Residence_type = 1 if stroke_data[0][6] == 'Urban' else 0
                avg_glucose_level = float(stroke_data[0][7])
                bmi = float(stroke_data[0][8])
                type_smoking_status = 3 if stroke_data[0][9] == 'smokes' else 2 if stroke_data[0][9] == 'never smoked' else 1 if stroke_data[0][9] == 'formerly smoked' else 0

                processing_data = np.array([[gender, age, hypertension, heart_disease, ever_married, work_type, Residence_type, avg_glucose_level, bmi, type_smoking_status]])
                stroke_diagnosis = Other_diagnosis('STROKE', processing_data)
                diagnosis_outcome.append(stroke_diagnosis.predict())
                which_outcome.append(True)
            else:
                which_outcome.append(False)
                
            output = generate_table(now_id, diagnosis_outcome, which_outcome)
            output.print_table()

# widgets
# 左邊 (分上下)
left_top_frame = Frame(ws, bd=2, relief=SOLID, padx=10, pady=10)
left_middle_frame = Frame(ws, bd=2, relief=SOLID, padx=10, pady=10)
left_down_frame = Frame(ws, bd=2, relief=SOLID, padx=10, pady=10)

# =============================================================================
# 上面
Label(left_top_frame, text="Patient ID", font=('Times', 14)).grid(row=0, column=0, sticky=W, pady=10)
log_em = Entry(left_top_frame, width=15, font=('Times', 14))
print_btn = Button(left_top_frame, text='Output', font=('Times', 14), command=output_print)
register_btn = Button(left_top_frame, width=10, text='Register/Renew', font=('Times', 12), command=usr_sign_up)
login_btn = Button(left_top_frame, width=10, text='Login', font=('Times', 12), command=usr_load)
del_btn = Button(left_top_frame, width=10, text='Delete', font=('Times', 12), command=del_data)
# 下面
diagnosis_type = StringVar()
diagnosis_type.set('Diagnosis outcomes')
Label(left_middle_frame, textvariable=diagnosis_type, font=('Times', 14)).grid(row=0, column=0, pady=10)
clear_btn = Button(left_middle_frame, width=5, text='Clear', font=('Times', 12), command=clear_image)
diagnosis_outcome = StringVar()
text_outcome = Entry(left_middle_frame, textvariable = diagnosis_outcome, width=20, font=('Times', 14), state='disabled')

# 右邊 (只有一個)
right_frame = Frame(ws, bd=2, relief=SOLID, padx=10, pady=10)
# =============================================================================
# 腦部偵測
head_photo = PhotoImage(file = "./Photo/head.png")
head_photo = head_photo.zoom(12)
head_photo = head_photo.subsample(30)
head_button = Button(right_frame, width=80, height = 50, image = head_photo, command = brain)
# 胸腔偵測
chest_photo = PhotoImage(file = "./Photo/chest.png")
chest_photo = chest_photo.zoom(10)
chest_photo = chest_photo.subsample(30)
chest_button = Button(right_frame, width=120, height = 80, image = chest_photo, command = chest)
# 皮膚偵測
skin_photo = PhotoImage(file = "./Photo/skin.png")
skin_photo = skin_photo.zoom(10)
skin_photo = skin_photo.subsample(30)
skin_button = Button(right_frame, width=40, height = 80, image = skin_photo, command = skin)
# 其他偵測
body_photo = PhotoImage(file = "./Photo/body.png")
body_photo = body_photo.zoom(10)
body_photo = body_photo.subsample(30)
body_button = Button(right_frame, width=120, height = 200, image = body_photo, command = body)

# widgets placement
# 左邊
# 上
log_em.grid(row=0, column=1, pady=10, padx=20)
print_btn.grid(row=0, column=2, pady=10, padx=20)
register_btn.grid(row=2, column=0, pady=10, padx=5)
login_btn.grid(row=2, column=1, pady=10, padx=5)
del_btn.grid(row=2, column=2, pady=10, padx=5)
left_top_frame.place(x=40, y=50)
# 中
text_outcome.grid(row=0, column=1, pady=0, padx=20)
clear_btn.grid(row=0, column=2, pady=0, padx=0)
left_middle_frame.place(x=40, y = 190)
# 下
Label(left_down_frame, text="Brain", font=('Times', 16)).grid(row=0, column=0, padx = 48, pady=58)
Label(left_down_frame, text='Chest', font=('Times', 16)).grid(row=0, column=1, padx = 48, pady=58)
Label(left_down_frame, text='Skin', font=('Times', 16)).grid(row=0, column=2, padx = 48, pady=58)
left_down_frame.place(x=40, y = 275)

# 右邊
head_button.grid(row=0, column=2, pady=0, padx=0, sticky = 'N')
chest_button.grid(row=1, column=2, pady=0, padx=60, sticky = 'N')
skin_button.grid(row=2, column=2, pady=0, padx=40, sticky = 'NW')
body_button.grid(row=2, column=2, pady=0, padx=40, sticky = 'NE')

right_frame.place(x=520, y=50)

# infinite loop
ws.mainloop()