from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.label import Label

class ReceiptLayout(BoxLayout):
    def submit_receipt(self):
        print("Submitted Receipt!")
        print("Location:", self.ids.purchase_location.text)
        print("Amount:", self.ids.purchase_amount.text)
        print("For:", self.ids.for_input.text)
        print("Project #:", self.ids.project_input.text)

        self.ids.purchase_location.text = ""
        self.ids.purchase_amount.text = ""
        self.ids.for_input.text = ""
        self.ids.project_input.text = ""


    def open_camera(self):
        from kivy.core.camera import Camera as CoreCamera  # Force import

        try:
            # Force index 0 (your webcam) and GStreamer backend
            camera = Camera(index=0, play=True, resolution=(640, 480), size_hint=(1, 0.8))
        except Exception as e:
            print("Camera init failed:", str(e))
            error_label = Label(text=f"Camera error: {str(e)}\n\nTry:\n- Plug in a webcam\n- Check permissions\n- Run 'sudo apt install gstreamer1.0-plugins-good'", halign='center')
            popup = Popup(title='Camera Issue', content=error_label, size_hint=(0.6, 0.4))
            popup.open()
            return

        capture_btn = Button(text='Capture Receipt', size_hint=(1, 0.2), background_color=(0, 0.8, 0.4, 1))
        capture_btn.bind(on_press=lambda x: self.capture_photo(camera))

        cam_layout = BoxLayout(orientation='vertical')
        cam_layout.add_widget(camera)
        cam_layout.add_widget(capture_btn)

        popup = Popup(title='Snap Receipt Photo', content=cam_layout, size_hint=(0.9, 0.9))
        popup.open()

    def capture_photo(self, camera):
        # Save photo
        camera.export_to_png('receipt_photo.png')
        print("Photo snapped! Saved as receipt_photo.png in project folder")
        # Optional: close popup or show preview later
        print("You can view it now!")

class ReceiptApp(App):
    def build(self):
        return ReceiptLayout()

if __name__ == '__main__':
    ReceiptApp().run()