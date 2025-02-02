#include <FastLED.h>
#include <string.h>

#define NUM_SIDE_LIGHTS 5
#define PIN_SIDE_LIGHTS 3

#define NUM_SCREEN_LIGHTS 5
#define PIN_SCREEN_LIGHTS 9

#define PIN_MAIN_LIGHT_1 5
#define PIN_MAIN_LIGHT_2 6

bool isFadingIn = false;
bool isFadingOut = false;
int currentBrightnessSideLight = 0;
int previousBrightnessSideLight = 0;
int nextBrightnessSideLight = 0;
int BrightnessSideLightAlpha = 255;
int maxBrightnessSideLight = 128;

int currentBrightnessMainLight = 0;
int previousBrightnessMainLight = 0;
int nextBrightnessMainLight = 0;
int BrightnessMainLightAlpha = 255;
int maxBrightnessMainLight = 128;
bool mainLightOverride = false;

CRGB previousColour = CRGB::Black;
CRGB currentColour = CRGB::Black;
CRGB nextColour = CRGB::Black;
int colourChangeAlpha = 255;

CRGB defaultColour = CRGB::White;
ColorTemperature colourTemps[9] = {ColorTemperature::Candle, ColorTemperature::Tungsten40W, ColorTemperature::Tungsten100W, ColorTemperature::Halogen, ColorTemperature::CarbonArc, ColorTemperature::HighNoonSun, ColorTemperature::DirectSunlight, ColorTemperature::OvercastSky, ColorTemperature::ClearBlueSky};

CRGB sideLeds[NUM_SIDE_LIGHTS];
CRGB screenLeds[NUM_SCREEN_LIGHTS];

void setup() { 
  Serial.begin(15200);
  previousColour = defaultColour;
  nextColour = defaultColour;
  FastLED.addLeds<WS2811, PIN_SIDE_LIGHTS, BRG>(sideLeds, NUM_SIDE_LIGHTS);
  FastLED.addLeds<WS2811, PIN_SCREEN_LIGHTS, BRG>(screenLeds, NUM_SCREEN_LIGHTS);
  changeAllLEDs(defaultColour);
  FastLED.setMaxPowerInMilliWatts(12000);
  FastLED.setBrightness(0);

  pinMode(PIN_MAIN_LIGHT_1, OUTPUT);
  pinMode(PIN_MAIN_LIGHT_2, OUTPUT);
}

void changeAllLEDs(CRGB newColour)
{
    FastLED.clear();
    for(int i = 0; i < NUM_SIDE_LIGHTS; i++)
    {
      sideLeds[i] = newColour;
    }
    for(int i = 0; i < NUM_SCREEN_LIGHTS; i++)
    {
      screenLeds[i] = newColour;
    }
}

void StartFadeIn()
{
  DefaultColour();
  isFadingIn = true;
  isFadingOut = false;
  BrightnessSideLightAlpha = 0;
  previousBrightnessSideLight = currentBrightnessSideLight;
  nextBrightnessSideLight = maxBrightnessSideLight;

  BrightnessMainLightAlpha = 0;
  previousBrightnessMainLight = currentBrightnessMainLight;
  nextBrightnessMainLight = maxBrightnessMainLight;
}

void StartFadeOut()
{
  DefaultColour();
  isFadingIn = false;
  isFadingOut = true;
  BrightnessSideLightAlpha = 0;
  previousBrightnessSideLight = currentBrightnessSideLight;
  nextBrightnessSideLight = 0;
  
  if(mainLightOverride == false)
  {
    BrightnessMainLightAlpha = 0;
    previousBrightnessMainLight = currentBrightnessMainLight;
    nextBrightnessMainLight = 0;
  }
}
void lightsOn()
{
  mainLightOverride = true;
  ChangeBrightnessMainLight(maxBrightnessMainLight);
}

void lightsOff()
{
  mainLightOverride = false;
  ChangeBrightnessMainLight(maxBrightnessMainLight);
}

void lightsAuto()
{
  mainLightOverride = false;
  ChangeBrightnessMainLight(maxBrightnessMainLight);
}

void ChangeColour(int r, int g, int b)
{
  previousColour = currentColour;
  nextColour = CRGB(r, g, b);
  colourChangeAlpha = 0;
}

void DefaultColour()
{
  previousColour = currentColour;
  nextColour = defaultColour;
  colourChangeAlpha = 0;
}

void ChangeBrightnessSideLight(int newBrightnessSideLight)
{
  maxBrightnessSideLight = newBrightnessSideLight;
  previousBrightnessSideLight = currentBrightnessSideLight;
  nextBrightnessSideLight = map(newBrightnessSideLight, 0, 100, 0, 255);
  StartFadeIn();
}

void ChangeBrightnessMainLight(int newBrightnessMainLight)
{
  if(mainLightOverride == false)
  {
    maxBrightnessMainLight = newBrightnessMainLight;
    previousBrightnessMainLight = currentBrightnessMainLight;
    nextBrightnessMainLight = map(newBrightnessMainLight, 0, 100, 0, 255);
    StartFadeIn();
  }
}

void ChangeWarmth(int newWarmth)
{
  ColorTemperature temp = colourTemps[map(newWarmth, 0, 100, 8, 0)];
  defaultColour = CRGB(temp);
  DefaultColour();
}

bool checkFirstThree(String str, String checkStr)
{
  return ((str[0] == checkStr[0]) && (str[1] == checkStr[1]) && (str[2] == checkStr[2]));
}

void loop() {
  String serialData = "";
  if(Serial.available() > 0) {
    serialData = Serial.readStringUntil('\n');
  }

  if (serialData != "") {

    Serial.println("In: " + serialData);

    if (serialData == "asd")
    {
      Serial.println("garbage!");
      Serial.flush();
    }
    else if (serialData == "fadeIn") 
    {
      StartFadeIn();
      Serial.println(serialData);
      Serial.flush();
    }
    else if (serialData == "fadeOut") 
    {
      StartFadeOut();
      Serial.println(serialData);
      Serial.flush();
    }
    else if (serialData == "mainLightsOn") 
    {
      lightsOn();
      Serial.println(serialData);
      Serial.flush();
    }
    else if (serialData == "mainLightsOff") 
    {
      lightsOff();
      Serial.println(serialData);
      Serial.flush();
    }
    else if (serialData == "mainLightsAuto") 
    {
      lightsAuto();
      Serial.println(serialData);
      Serial.flush();
    }
    else if (checkFirstThree(serialData, "RGB") == true)
    {
      //default colour
      if((serialData[3] == 'D') && (serialData[4] == 'E') && (serialData[5] == 'F'))
      {
        DefaultColour();
        Serial.println(serialData);
        Serial.flush();
      }
      else
      {
        //colour
        Serial.println(serialData);
        Serial.flush();
        int r, g, b;
        String rStr = String(serialData).substring(4,6);
        String gStr = String(serialData).substring(6,8);
        String bStr = String(serialData).substring(8,10);
        const char* rCha = rStr.c_str();
        const char* gCha = gStr.c_str();
        const char* bCha = bStr.c_str();
        r = (int)strtol(rCha, NULL, 16);
        g = (int)strtol(gCha, NULL, 16);
        b = (int)strtol(bCha, NULL, 16);
        ChangeColour(r, g, b);
      }
    }
    else if (checkFirstThree(serialData, "MBR") == true)
    {
      //BrightnessMainLight
      String temp = "";
      for(int i = 3; i < serialData.length(); i++)
      {
        temp += serialData[i];
      }
      Serial.println(serialData);
      Serial.flush();
      ChangeBrightnessMainLight(temp.toInt());
      
    }
    else if (checkFirstThree(serialData, "SBR") == true)
    {
      //BrightnessSideLight
      String temp = "";
      for(int i = 3; i < serialData.length(); i++)
      {
        temp += serialData[i];
      }
      Serial.println(serialData);
      Serial.flush();
      ChangeBrightnessSideLight(temp.toInt());
      
    }
    else if (checkFirstThree(serialData, "WAR") == true)
    {
      //Warmth
      String temp = "";
      for(int i = 3; i < serialData.length(); i++)
      {
        temp += serialData[i];
      }
      Serial.println(serialData);
      Serial.flush();
      ChangeWarmth(temp.toInt());
      
    }
    else if (checkFirstThree(serialData, "MLO") == true)
    {
      if(serialData[3] == '1')
      {
        lightsOn();
      }
      else
      {
        lightsOff();
      }
    }

  }

  if(BrightnessSideLightAlpha < 255)
  {
    currentBrightnessSideLight = map(BrightnessSideLightAlpha, 0, 254, previousBrightnessSideLight, nextBrightnessSideLight);
    BrightnessSideLightAlpha++;
  }

  if(BrightnessMainLightAlpha < 255)
  {
    currentBrightnessMainLight = map(BrightnessMainLightAlpha, 0, 254, previousBrightnessMainLight, nextBrightnessMainLight);
    BrightnessMainLightAlpha++;
  }
  
  if(colourChangeAlpha < 255)
  {
    currentColour.r = map(colourChangeAlpha, 0, 254, previousColour.r, nextColour.r);
    currentColour.g = map(colourChangeAlpha, 0, 254, previousColour.g, nextColour.g);
    currentColour.b = map(colourChangeAlpha, 0, 254, previousColour.b, nextColour.b);

    changeAllLEDs(currentColour);
    colourChangeAlpha++;
  }


  FastLED.setBrightness(currentBrightnessSideLight);
  FastLED.show();
  analogWrite(PIN_MAIN_LIGHT_1, currentBrightnessMainLight);
  analogWrite(PIN_MAIN_LIGHT_2, currentBrightnessMainLight);
  delay(5);
}
