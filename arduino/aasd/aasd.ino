#include <FastLED.h>
#include <string.h>

#define NUM_SIDE_LIGHTS 5
#define PIN_BAR_LIGHTS 3

#define NUM_SCREEN_LIGHTS 5
#define PIN_SCREEN_LIGHTS 9

#define PIN_MAIN_LIGHT_1 5
#define PIN_MAIN_LIGHT_2 6

#define NUM_INGREDIENT_LIGHTS_PER_STRIP 15
#define NUM_LEDS_PER_LIGHT 7
#define PIN_INGREDIENT_STRIP_1 10
#define PIN_INGREDIENT_STRIP_2 11

String serialData = "";

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

bool mainLightsOn = true;
bool barLightsOn = true;
bool screenLightsOn = true;

CRGB rainbow[7] = { CRGB::Red, CRGB::Orange, CRGB::Yellow, CRGB::Green, CRGB::Blue, CRGB::Indigo, CRGB::Violet };

int strip1currentBrightness[NUM_INGREDIENT_LIGHTS_PER_STRIP];
int strip2currentBrightness[NUM_INGREDIENT_LIGHTS_PER_STRIP];
int strip1nextBrightness[NUM_INGREDIENT_LIGHTS_PER_STRIP];
int strip2nextBrightness[NUM_INGREDIENT_LIGHTS_PER_STRIP];

CRGB previousColour = CRGB::Black;
CRGB currentColour = CRGB::Black;
CRGB nextColour = CRGB::Black;
int colourChangeAlpha = 255;

CRGB defaultColour = CRGB::White;
ColorTemperature colourTemps[9] = {ColorTemperature::Candle, ColorTemperature::Tungsten40W, ColorTemperature::Tungsten100W, ColorTemperature::Halogen, ColorTemperature::CarbonArc, ColorTemperature::HighNoonSun, ColorTemperature::DirectSunlight, ColorTemperature::OvercastSky, ColorTemperature::ClearBlueSky};

CRGB barLeds[NUM_SIDE_LIGHTS];
CRGB screenLeds[NUM_SCREEN_LIGHTS];
CRGB ingredientLeds1[NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT];
CRGB ingredientLeds2[NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT];

void setup() { 
  Serial.begin(2000000);
  while (!Serial) {
    ;
  }
  Serial.flush();
  Serial.setTimeout(5000);
  serialData.reserve(200);
  FastLED.setBrightness(255);
  
  previousColour = defaultColour;
  nextColour = defaultColour;
  FastLED.addLeds<WS2811, PIN_BAR_LIGHTS, BRG>(barLeds, NUM_SIDE_LIGHTS);
  FastLED.addLeds<WS2811, PIN_SCREEN_LIGHTS, BRG>(screenLeds, NUM_SCREEN_LIGHTS);
  
  FastLED.addLeds<WS2811, PIN_INGREDIENT_STRIP_1, GRB>(ingredientLeds1, NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT);
  FastLED.addLeds<WS2811, PIN_INGREDIENT_STRIP_2, GRB>(ingredientLeds2, NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT);
  
  for(int i = 0; i < NUM_INGREDIENT_LIGHTS_PER_STRIP; i++)
  {
      strip1currentBrightness[i] = 0;
      strip2currentBrightness[i] = 0;
  }
  clearAllIngredients();

  updateSideAndScreenLEDs();
  //FastLED.setMaxPowerInMilliWatts(12000);
  

  pinMode(PIN_MAIN_LIGHT_1, OUTPUT);
  pinMode(PIN_MAIN_LIGHT_2, OUTPUT);
  pinMode(PIN_BAR_LIGHTS, OUTPUT);
  pinMode(PIN_SCREEN_LIGHTS, OUTPUT);
  pinMode(PIN_INGREDIENT_STRIP_1, OUTPUT);
  pinMode(PIN_INGREDIENT_STRIP_2, OUTPUT);
}

void clearAllIngredients()
{
  for(int i = 0; i < NUM_INGREDIENT_LIGHTS_PER_STRIP; i++)
  {
      strip1nextBrightness[i] = 0;
      strip2nextBrightness[i] = 0;
  }
}

void setIngredientOn(int strip, int index)
{
  if(strip == 0)
  {
    strip1nextBrightness[index] = 255;
  }
  else if(strip == 1)
  {
      strip2nextBrightness[index] = 255;
  }
}

void updateSideAndScreenLEDs()
{
    for(int i = 0; i < NUM_SIDE_LIGHTS; i++)
    {
      if(barLightsOn == true)
      {
        barLeds[i] = getColourWithBrightness(currentColour, currentBrightnessSideLight);
      }
      else
      {
        barLeds[i] = CRGB::Black;
      }
    }
    for(int i = 0; i < NUM_SCREEN_LIGHTS; i++)
    {
      if(screenLightsOn == true)
      {
        screenLeds[i] = getColourWithBrightness(currentColour, currentBrightnessSideLight);
      }
      else
      {
        screenLeds[i] = CRGB::Black;
      }
    }
}

CRGB getColourWithBrightness(CRGB colour, int brightness)
{
    int r = map(brightness, 0, 255, 0, colour.r);
    int g = map(brightness, 0, 255, 0, colour.g);
    int b = map(brightness, 0, 255, 0, colour.b);
    return CRGB(r, g, b);
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

void checkSerialData(String serialData)
{

    

    if (serialData == "asd" || serialData == "asdasd")
    {
      Serial.print("garbage!\n");
      Serial.flush();
      return;
    }
    else if (serialData == "fadeIn") 
    {
      StartFadeIn();
      Serial.print("Do FadeIn\n");
      Serial.flush();
      return;
    }
    else if (serialData == "fadeOut") 
    {
      StartFadeOut();
      Serial.print("Do FadeOut\n");
      Serial.flush();
      return;
    }
    else if (serialData == "mainLightsOn") 
    {
      lightsOn();
      Serial.print("Do Main Lights On\n");
      Serial.flush();
      return;
    }
    else if (serialData == "mainLightsOff") 
    {
      lightsOff();
      Serial.print("Do Main Lights Off\n");
      Serial.flush();
      return;
    }
    else if (serialData == "mainLightsAuto") 
    {
      lightsAuto();
      Serial.print("Do Main Lights Auto\n");
      Serial.flush();
      return;
    }
    else if (checkFirstThree(serialData, "RGB") == true)
    {
      //default colour
      if((serialData[3] == 'D') && (serialData[4] == 'E') && (serialData[5] == 'F'))
      {
        DefaultColour();
        Serial.print("Default colour\n");
        Serial.flush();
        return;
      }
      else
      {
        //colour
        Serial.print("Custom colour: " + String(serialData).substring(4,6) + String(serialData).substring(6,8) + String(serialData).substring(8,10) + "\n");
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
        return;
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
      Serial.print("Main Lights Brightness\n");
      Serial.flush();
      ChangeBrightnessMainLight(temp.toInt());
      return;
    }
    else if (checkFirstThree(serialData, "SBR") == true)
    {
      //BrightnessSideLight
      String temp = "";
      for(int i = 3; i < serialData.length(); i++)
      {
        temp += serialData[i];
      }
      Serial.print("Side Lights Brightness\n");
      Serial.flush();
      ChangeBrightnessSideLight(temp.toInt());
      return;
    }
    else if (checkFirstThree(serialData, "WAR") == true)
    {
      //Warmth
      String temp = "";
      for(int i = 3; i < serialData.length(); i++)
      {
        temp += serialData[i];
      }
      Serial.print("Warmth\n");
      Serial.flush();
      ChangeWarmth(temp.toInt());
      return;
    }
    else if (checkFirstThree(serialData, "MLO") == true)
    {
      Serial.print("Main Lights Override\n");
      Serial.flush();
      if(serialData[3] == '1')
      {
        lightsOn();
      }
      else
      {
        lightsOff();
      }
      return;
    }
    else if (checkFirstThree(serialData, "BLC") == true)
    {
      Serial.print("Bar Lights On/Off\n");
      Serial.flush();
      if(serialData[3] == '1')
      {
        barLightsOn = true;
      }
      else
      {
        barLightsOn = false;
      }
      return;
    }
    else if (checkFirstThree(serialData, "MLC") == true)
    {
      Serial.print("Main Lights On/Off\n");
      Serial.flush();
      if(serialData[3] == '1')
      {
        mainLightsOn = true;
      }
      else
      {
        mainLightsOn = false;
      }
      return;
    }
    else if (checkFirstThree(serialData, "SLC") == true)
    {
      Serial.print("Side Lights On/Off\n");
      Serial.flush();
      if(serialData[3] == '1')
      {
        screenLightsOn = true;
      }
      else
      {
        screenLightsOn = false;
      }
      return;
    }
    
    else if (checkFirstThree(serialData, "ING") == true)
    {
      Serial.print("Ingredient Lights\n");
      Serial.flush();

      clearAllIngredients();
      if(serialData.length() <= 3)
      {
        return;
      }
      //ING1:2|2:5|1:10
      String tempStrip = "";
      String tempIndex = "";
      bool PassedColon = false;
      for(int i = 3; i <= serialData.length(); i++)
      {
        if(serialData[i] == ':')
        {
          PassedColon = true;
          continue;
        }
        if((serialData[i] == '|') || (i == serialData.length()))
        {
          PassedColon = false;
          setIngredientOn(tempStrip.toInt(), tempIndex.toInt());
          tempStrip = "";
          tempIndex = "";
          continue;
        }

        if(PassedColon == false)
        {
          tempStrip += serialData[i];
        }
        else
        {
          tempIndex += serialData[i];
        }
      }
    }
    
}

bool commandStarted = false;
void loop() {
  

  if (Serial.available()) {

    char inChar = (char)Serial.read();

    if(commandStarted == false)
    {
      if(inChar == '<')
      {
        commandStarted = true;
        serialData = "";
      }
    }
    else
    {
      if(inChar == '>')
      {
        commandStarted = false;
        String ret = "data: " + serialData + "\n";
        Serial.write(ret.c_str());
        Serial.flush();
        serialData = "";
      }
      else
      {
        serialData += inChar;
      }

    }

      //checkSerialData(serialData);

  }

  //if(Serial.available() > 0) {
  //  serialData = Serial.readStringUntil('\n');
  //  serialData.trim();
  //  checkSerialData(serialData);
  //}

  FastLED.clear();

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
    colourChangeAlpha++;
  }

  for(int i = 0; i < NUM_INGREDIENT_LIGHTS_PER_STRIP; i++)
  {
    if(strip1nextBrightness[i] > strip1currentBrightness[i])
    {
      strip1currentBrightness[i] = min(strip1currentBrightness[i] + 3, 255);
      //strip1currentBrightness[i]++;
    }
    else if(strip1nextBrightness[i] < strip1currentBrightness[i])
    {
      strip1currentBrightness[i] = max(strip1currentBrightness[i] - 3, 0);
      //strip1currentBrightness[i]--;
    }
    int r = map(strip1currentBrightness[i], 0, 255, 0, defaultColour.r);
    int g = map(strip1currentBrightness[i], 0, 255, 0, defaultColour.g);
    int b = map(strip1currentBrightness[i], 0, 255, 0, defaultColour.b);
    for(int j = 0; j < NUM_LEDS_PER_LIGHT; j++)
    {
      ingredientLeds1[(i * NUM_LEDS_PER_LIGHT) + j] = CRGB(r, g, b);
    }

    if(strip2nextBrightness[i] > strip2currentBrightness[i])
    {
      strip2currentBrightness[i] = min(strip2currentBrightness[i] + 5, 255);
      //strip2currentBrightness[i]++;
    }
    else if(strip2nextBrightness[i] < strip2currentBrightness[i])
    {
      strip2currentBrightness[i] = max(strip2currentBrightness[i] - 2, 0);
      //strip2currentBrightness[i]--;
    }
    r = map(strip2currentBrightness[i], 0, 255, 0, defaultColour.r);
    g = map(strip2currentBrightness[i], 0, 255, 0, defaultColour.g);
    b = map(strip2currentBrightness[i], 0, 255, 0, defaultColour.b);
    for(int j = 0; j < NUM_LEDS_PER_LIGHT; j++)
    {
      ingredientLeds2[(i * NUM_LEDS_PER_LIGHT) + j] = CRGB(r, g, b);
    }
    
  }

  updateSideAndScreenLEDs();
  FastLED.show();

  if(mainLightsOn == true)
  {
    analogWrite(PIN_MAIN_LIGHT_1, currentBrightnessMainLight);
    analogWrite(PIN_MAIN_LIGHT_2, currentBrightnessMainLight);
  }
  else
  {
    analogWrite(PIN_MAIN_LIGHT_1, 0);
    analogWrite(PIN_MAIN_LIGHT_2, 0);
  }
  //delay(5);
}
