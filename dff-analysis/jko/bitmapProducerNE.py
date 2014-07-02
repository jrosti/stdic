

import Image
import wx

global bitmap

pilImage = Image.open('lena.png').rotate(135)
image = wx.EmptyImage(pilImage.size[0],pilImage.size[1])
image.SetData(pilImage.convert("RGB").tostring())
#image.setAlphaData(pil.convert("RGBA").tostring()[3::4]

## use the wx.Image or convert it to wx.Bitmap
bitmap = wx.BitmapFromImage(image)