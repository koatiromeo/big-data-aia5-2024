import customtkinter
from PIL import Image
import os
import requests
import tkinter.ttk as ttk
from tkinter import messagebox
#customtkinter.set_appearance_mode("dark")

access_token = ""

class App(customtkinter.CTk):
    width = 900
    height = 600

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Login")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)

        # load and create background image
        current_path = os.path.dirname(os.path.realpath(__file__))
        self.bg_image = customtkinter.CTkImage(Image.open(current_path + "/images/police1.jpeg"),
                                               size=(self.width, self.height))
        self.bg_image_label = customtkinter.CTkLabel(self, image=self.bg_image)
        self.bg_image_label.grid(row=0, column=0)

        # create login frame
        self.login_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent", bg_color="transparent")
        self.login_frame.grid(row=0, column=0, sticky="ns")
        self.login_label = customtkinter.CTkLabel(self.login_frame, text="Page d'identification\n\nLogin Page",
                                                  font=customtkinter.CTkFont(size=20, weight="bold"))
        #self.login_frame.pack_forget()
        self.login_label.grid(row=0, column=0, padx=30, pady=(150, 15))
        self.username_entry = customtkinter.CTkEntry(self.login_frame, width=200, placeholder_text="username")
        self.username_entry.grid(row=1, column=0, padx=30, pady=(15, 15))
        self.password_entry = customtkinter.CTkEntry(self.login_frame, width=200, show="*", placeholder_text="password")
        self.password_entry.grid(row=2, column=0, padx=30, pady=(0, 15))
        self.login_button = customtkinter.CTkButton(self.login_frame, text="Login", command=self.login_event, width=200)
        self.login_button.grid(row=3, column=0, padx=30, pady=(15, 15))
        
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.login_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=8, column=0, padx=20, pady=20, sticky="s")
        
        
        # formulaire d'ajout des CNI...
        self.add_cni_form_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.add_cni_form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.add_cni_form_frame.grid_forget()  # Masquer le formulaire initialement
        self.add_cni_label = customtkinter.CTkLabel(self, text="Formulaire d'ajout CNI",
                                                    font=customtkinter.CTkFont(size=15, weight="bold"))
        self.add_cni_label.grid(row=0, column=0, padx=30, pady=(10, 15))
        self.nom_entry = customtkinter.CTkEntry(self, width=200, placeholder_text="Nom")
        self.nom_entry.grid(row=1, column=0, padx=30, pady=(0, 15))
        self.prenom_entry = customtkinter.CTkEntry(self, width=200, placeholder_text="Prénom")
        self.prenom_entry.grid(row=2, column=0, padx=30, pady=(0, 15))
        self.date_naissance_entry = customtkinter.CTkEntry(self, width=200, placeholder_text="Date de Naissance")
        self.date_naissance_entry.grid(row=3, column=0, padx=30, pady=(0, 15))
        self.add_cni_button = customtkinter.CTkButton(self, text="Ajouter CNI", command=self.add_cni_event, width=200)
        self.add_cni_button.grid(row=4, column=0, padx=30, pady=(15, 15))
        # fin formulaire
        
        
    def add_cni_event(self):
        # Obtenez les valeurs du formulaire
        nom = self.nom_entry.get()
        prenom = self.prenom_entry.get()
        date_naissance = self.date_naissance_entry.get()
        
        # Validez les valeurs (ajoutez des validations supplémentaires selon vos besoins)
        if not nom or not prenom or not date_naissance:
            messagebox.showwarning(title="Warning", message="Veuillez remplir tous les champs.")
            return

        # Envoyez les données au serveur (ajoutez la logique de l'API appropriée)
        try:
            api_url = 'http://192.168.0.100:5000/add_cni'
            headers = {'Authorization': f'Bearer {access_token}'}
            data = {'nom': nom, 'prenom': prenom, 'date_naissance': date_naissance}
            response = requests.post(api_url, headers=headers, json=data)

            if response.status_code == 200:
                messagebox.showinfo(title="Succès", message="CNI ajoutée avec succès.")
                # Effacez les champs du formulaire après l'ajout réussi
                self.nom_entry.delete(0, "end")
                self.prenom_entry.delete(0, "end")
                self.date_naissance_entry.delete(0, "end")
            else:
                messagebox.showwarning(title="Erreur", message="Échec de l'ajout de CNI. Veuillez réessayer plus tard.")

        except Exception as e:
            messagebox.showwarning(title="Erreur", message="Une erreur critique s'est produite. Veuillez réessayer plus tard.")
        

    def login_event(self):
        global access_token
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        api_url = 'http://192.168.0.100:5000/login_manager'
        
        data = {'username': username, 'password': password}
        response = requests.post(api_url, json=data)


        if response.status_code == 200:
            print("Login ok" )
            data_info = response.json()
            access_token = data_info["access_token"]
            print("la valeur recu", access_token)
            # Afficher la prochaine page (dans cet exemple, c'est une simple page de confirmation)
            self.destroy()
            confirmation_page = ConfirmationPage()
            confirmation_page.mainloop()  # Open the second page
        else:
            # Ajouter un label pour afficher les erreurs dans le main_frame
            self.error_label = customtkinter.CTkLabel(self.login_frame, text="Invalid username or password", text_color= "red", font=customtkinter.CTkFont(size=12))
            self.error_label.grid(row=0, column=0, padx=30, pady=(30, 15))  # Positionnez-le en fonction de vos besoins
            
    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

       



class ConfirmationPage(customtkinter.CTk):
    width = 700
    height = 450
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Administration")
        self.geometry(f"{self.width}x{self.height}")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "police1.jpeg")), size=(26, 26))
        self.drapeau = customtkinter.CTkImage(Image.open(os.path.join(image_path, "drapeau.jpg")), size=(500, 150))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.liste = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "liste.jpg")),
                                                 dark_image=Image.open(os.path.join(image_path, "liste.jpg")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))
        self.modifier = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "modifier.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "modifier.png")), size=(20, 20))
        self.supprimer = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "supprimer.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "supprimer.png")), size=(20, 20))
        self.reconnaissance = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "reconnaissance.jpg")),
                                                     dark_image=Image.open(os.path.join(image_path, "reconnaissance.jpg")), size=(20, 20))
        self.reco = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "reco.jpg")),
                                                     dark_image=Image.open(os.path.join(image_path, "reco.jpg")), size=(20, 20))
        
    

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(6, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Bienvenue", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        #liste CNI
        
        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Liste des CNI",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.liste, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Ajouter CNI",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")
        
        self.frame_4_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Modifier CNI",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.modifier, anchor="w", command=self.frame_4_button_event)
        self.frame_4_button.grid(row=4, column=0, sticky="ew")
        
        self.frame_5_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Supprimer CNI",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.supprimer, anchor="w", command=self.frame_5_button_event)
        self.frame_5_button.grid(row=5, column=0, sticky="ew")
        
        self.frame_6_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Detection de faces",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.reconnaissance, anchor="w", command=self.frame_6_button_event)
        self.frame_6_button.grid(row=6, column=0, sticky="ew")
        
        self.frame_7_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Face matching",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.reco, anchor="w", command=self.frame_7_button_event)
        self.frame_7_button.grid(row=7, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=8, column=0, padx=20, pady=20, sticky="s")

        # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.home_frame_large_image_label = customtkinter.CTkLabel(self.home_frame, text="", image=self.drapeau)
        self.home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)

        self.home_frame_button_1 = customtkinter.CTkButton(self.home_frame, text="Frame 2", image=self.image_icon_image)
        self.home_frame_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.home_frame_button_2 = customtkinter.CTkButton(self.home_frame, text="Frame 3", image=self.image_icon_image, compound="right")
        self.home_frame_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.home_frame_button_3 = customtkinter.CTkButton(self.home_frame, text="Frame 4", image=self.image_icon_image, compound="top")
        self.home_frame_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.home_frame_button_4 = customtkinter.CTkButton(self.home_frame, text="Frame 5", image=self.image_icon_image, compound="bottom", anchor="w")
        self.home_frame_button_4.grid(row=4, column=0, padx=20, pady=10)

        # create second frame
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # create third frame
        self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        
        # create four frame
        self.four_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        
        # create five frame
        self.five_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # select default frame
        self.select_frame_by_name("home")
              
           

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")
        self.frame_4_button.configure(fg_color=("gray75", "gray25") if name == "frame_4" else "transparent")
        self.frame_5_button.configure(fg_color=("gray75", "gray25") if name == "frame_5" else "transparent")
        self.frame_6_button.configure(fg_color=("gray75", "gray25") if name == "frame_6" else "transparent")
        self.frame_7_button.configure(fg_color=("gray75", "gray25") if name == "frame_7" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "frame_2":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()
        if name == "frame_3":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()
        if name == "frame_4":
            self.four_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.four_frame.grid_forget()
        if name == "frame_5":
            self.five_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.five_frame.grid_forget()
        if name == "frame_6":
            self.five_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.five_frame.grid_forget()
        if name == "frame_7":
            self.five_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.five_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")
        global access_token
        try:
            # Make a GET request to the API to retrieve all users
            api_url = 'http://192.168.0.100:5000/cnis'
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(api_url, headers=headers)

           
            if response.status_code == 200:
                cnis_data = response.json()
                # Créez un frame pour le tableau des CNI
                self.cni_table_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
                self.cni_table_frame.grid(row=0, column=1, sticky="nsew")
                
                # Dans cet exemple, j'utilise un Treeview pour le tableau
                self.cni_table = ttk.Treeview(self.cni_table_frame, columns=("ID", "Nom", "Prénom", "DateDeNaissance"))
                self.cni_table.heading("ID", text="ID")
                self.cni_table.heading("Nom", text="Nom")
                self.cni_table.heading("Prénom", text="Prénom")
                self.cni_table.heading("DateDeNaissance", text="Date de naissance")
                # Insertion de données fictives dans le Treeview
                for elt in cnis_data:
                    self.cni_table.insert(cnis_data["carte_id"], cnis_data["nom"], cnis_data["prenom"], cnis_data["date_naissance"])
                    
                #self.cni_table.grid(row=0, column=0, sticky="nsew")
                self.cni_table.pack(padx=10, pady=10, fill="both", expand=True)
            else:
                messagebox.showwarning(title = "Warning", message = "Une erreur s'est produite, veillez reessayer plus tard.")

        except Exception as e:
            # Handle any exception that might occur during the request
            messagebox.showwarning(title = "Warning", message = "Une erreur critique et tres grave s'est produite, veillez reessayer plus tard.")
            
        
 
 
        


    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")
        self.add_cni_form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.cni_table_frame.grid_forget()
        
    def frame_4_button_event(self):
        self.select_frame_by_name("frame_4")
        
    def frame_5_button_event(self):
        self.select_frame_by_name("frame_5")
        
    def frame_6_button_event(self):
        self.select_frame_by_name("frame_6")
        
    def frame_7_button_event(self):
        self.select_frame_by_name("frame_7")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)
        
    

if __name__ == "__main__":
    app = App()
    app.mainloop()
