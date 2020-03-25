from geeteventbus.event import event
from pynput import mouse, keyboard

class UserInput():
    """Connects the user input to classes that need it or actions that are triggered by it"""

    def __init__(self,bus):
        self.bus = bus
        touch_listener = mouse.Listener(on_click=self.on_touch)
        touch_listener.start()
        self.touch_listener = touch_listener
        keyboard_listener = keyboard.Listener(on_press=self.on_keyboard_key_press)
        keyboard_listener.start()
        self.keyboard_listener = keyboard_listener

    def on_touch(self,x,y,button,pressed):
        if(pressed):
            self.bus.post(event('touch',(x,y)))

    def on_keyboard_key_press(self,key):
        #adjustements
        if(key == keyboard.KeyCode.from_char('a')):
            self.bus.post(event('adjust','left'))
        elif(key == keyboard.KeyCode.from_char('d')):
            self.bus.post(event('adjust','right'))
        elif(key == keyboard.KeyCode.from_char('w')):
            self.bus.post(event('adjust','up'))
        elif(key == keyboard.KeyCode.from_char('s')):
            self.bus.post(event('adjust','down'))
        #zooms
        elif(key == keyboard.KeyCode.from_char('q')):
            self.bus.post(event('zoom','in'))
        elif(key == keyboard.KeyCode.from_char('e')):
            self.bus.post(event('zoom','out'))
        #temp bindings for testing
        elif(key == keyboard.KeyCode.from_char('z')):
            self.bus.post(event('crosshair','next'))
        elif(key == keyboard.KeyCode.from_char('1')):
            self.bus.post(event('crosshair',1))
        elif(key == keyboard.KeyCode.from_char('2')):
            self.bus.post(event('crosshair',2))
        elif(key == keyboard.KeyCode.from_char('3')):
            self.bus.post(event('crosshair',3))
        elif(key == keyboard.KeyCode.from_char('p')):
            self.bus.post(event('photo', ''))
