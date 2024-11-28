##This class loads your gif after splitting it into single frames. This uses a class called "imagesequencergb" so that the update loops through the rgb memory too.
##Use the original gif converter if you don't need color space changes for each frame. 

from PIL import Image
import io

inputFile = "pixilart-frames/pixil-frame-"
name = "ClassName"

frameCount = 22
class Frame:
    data = []

frameNames = []
frames = []
palette = []
w = 272
h = 92

def GetFrames(image):
    global palette, width, height
    for x in range(frameCount):
        #image.seek(x)
        Rimage = Image.open(inputFile + str(x) + ".png").convert("P", palette = Image.ADAPTIVE, colors = 255)
        
        #crop if needed.
        left = 0
        top = 0
        right = w
        bottom = h 

        Rimage = Rimage.crop((left, top, right, bottom))
        #Rimage.show()

        width, height = Rimage.size
        palette.append(Rimage.getpalette())
        rgbData = []

        for i in range(height):
            for j in range(width):
                index = Rimage.getpixel((j, i))

                rgbData.append(index)

        frame = Frame()
        frame.rgbData = rgbData
        frames.append(frame)
        
        #Rimage.save(outputPic + str(x) + ".png")

def GetHeader(className):
    
    data = "#include \"../../Assets/Textures/Animated/Utils/ImageSequenceRGB.h\"\n\n"

    data += "class " + className + "Sequence : public ImageSequenceRGB{\n"
    data += "private:\n"

    for i in range(len(frames)):
        data += "\tstatic const uint8_t frame" + str(i).rjust(4, '0') + "[];\n"

    data += "\n"

    for i in range(len(frames)):
        data += "\tstatic const uint8_t rgbColors" + str(i).rjust(4, '0') + "[];\n"

    data += "\n"

    data += "\tstatic const uint8_t* sequence[" + str(frameCount) + "];\n\n"

    data += "\n"

    data += "\tstatic const uint8_t* RGBsequence[" + str(frameCount) + "];\n\n"

    data += "\tImage image = Image(frame0000, rgbColors0000, " + str(w) + ", " + str(h) + ", "  + str(int(len(palette) / 3) - 1) + ");\n\n"
    data += "public:\n"
    data += "\t" + className + "Sequence(Vector2D size, Vector2D offset, float fps) : ImageSequenceRGB(&image, sequence, RGBsequence, (unsigned int)" + str(frameCount) + ", fps) {\n"
    data += "\t\timage.SetSize(size);\n"
    data += "\t\timage.SetPosition(offset);\n"
    data += "\t}\n"
    
    data += "};\n\n"
    return data

def GetCpp(className):
    data = "#include \"" + className + "Sequence.h\"\n\n"
    for i, frame in enumerate(frames):
        data += "const uint8_t " + className + "Sequence::frame" + str(i).rjust(4, '0') + "[] PROGMEM = {"

        for j, frameData in enumerate(frame.rgbData):
            data += str(frameData)
            
            if j + 1 != len(frame.rgbData):
                data += ","
            else:
                data += "};\n"

    data += "\nconst uint8_t* " + className + "Sequence::sequence[] = {"

    for i, frame in enumerate(frames):
        data += "frame" + str(i).rjust(4, '0')
        
        if i + 1 != len(frames):
            data += ","
        else:
            data += "};\n"

    for j, pal in enumerate(palette):
        data += "const uint8_t " + className + "Sequence::rgbColors" + str(j).rjust(4, '0') + "[] PROGMEM = {"
        for i in range(int(len(pal) / 3)):
            r = pal[i * 3]
            g = pal[i * 3 + 1]
            b = pal[i * 3 + 2]

            data += str(r) + "," + str(g) + "," + str(b)
            
            if i == len(pal) / 3 - 1:
                data += "};\n"
            else:
                data += ","

    data += "\nconst uint8_t* " + className + "Sequence::RGBsequence[] = {"

    for i, frame in enumerate(frames):
        data += "rgbColors" + str(i).rjust(4, '0')
        
        if i + 1 != len(frames):
            data += ","
        else:
            data += "};\n"

    return data


image = Image.open(inputFile + "0.png").convert("P", palette = Image.ADAPTIVE, colors = 255)

image.seek(0)

print("Number of frames: " + str(frameCount))
print("Number of palette colors: " + str(int(len(palette) / 3)))

GetFrames(image)#parse frame data

headerOutput = GetHeader(name)
cppOutput = GetCpp(name)

#print(headerOutput)
#print(cppOutput)
headerFile = open(name +"Sequence.h", "w")
headerFile.write(headerOutput)
headerFile.close()

cppFile = open(name +"Sequence.cpp", "w")
cppFile.write(cppOutput)
cppFile.close()
