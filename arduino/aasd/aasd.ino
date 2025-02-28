#include <FastLED.h>
#include <string.h>

#define NUM_BAR_LIGHTS 20
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


CRGB defaultColour = CRGB(ColorTemperature::Halogen);
ColorTemperature colourTemps[9] = {ColorTemperature::Candle, ColorTemperature::Tungsten40W, ColorTemperature::Tungsten100W, ColorTemperature::Halogen, ColorTemperature::CarbonArc, ColorTemperature::HighNoonSun, ColorTemperature::DirectSunlight, ColorTemperature::OvercastSky, ColorTemperature::ClearBlueSky};

CRGB previousColour = defaultColour;
CRGB currentColour = CRGB::Black;
CRGB nextColour = defaultColour;
int colourChangeAlpha = 255;

CRGB barLeds[NUM_BAR_LIGHTS];
CRGB screenLeds[NUM_SCREEN_LIGHTS];
CRGB ingredientLeds1[NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT];
CRGB ingredientLeds2[NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT];

void setup() { 
  Serial.begin(115200);
  while (!Serial) {
    ;
  }
  
  Serial.setTimeout(5000);
  FastLED.setBrightness(255);
  
  FastLED.addLeds<WS2811, PIN_BAR_LIGHTS, RGB>(barLeds, NUM_BAR_LIGHTS);
  FastLED.addLeds<WS2811, PIN_SCREEN_LIGHTS, BRG>(screenLeds, NUM_SCREEN_LIGHTS);
  
  FastLED.addLeds<WS2811, PIN_INGREDIENT_STRIP_1, BRG>(ingredientLeds1, NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT);
  FastLED.addLeds<WS2811, PIN_INGREDIENT_STRIP_2, BRG>(ingredientLeds2, NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT);
  
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

  analogWrite(PIN_MAIN_LIGHT_1, 0);
  analogWrite(PIN_MAIN_LIGHT_2, 0);
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
    for(int i = 0; i < NUM_BAR_LIGHTS; i++)
    {
      if(barLightsOn == true)
      {
        barLeds[i] = getColourWithBrightness(currentColour, currentBrightnessSideLight);
        //barLeds[i] = currentColour;
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

void sendSerialData(String data)
{
  Serial.println(data);
  Serial.flush();
}

void checkSerialData(String serialData)
{
    if (serialData == "asd" || serialData == "asdasd")
    {
      sendSerialData("garbage");
      return;
    }
    else if (serialData == "fadeIn") 
    {
      StartFadeIn();
      sendSerialData("Do FadeIn");
      return;
    }
    else if (serialData == "fadeOut") 
    {
      StartFadeOut();
      sendSerialData("Do FadeOut");
      return;
    }
    else if (serialData == "mainLightsOn") 
    {
      lightsOn();
      sendSerialData("Do Main Lights On");
      return;
    }
    else if (serialData == "mainLightsOff") 
    {
      lightsOff();
      sendSerialData("Do Main Lights Off");
      return;
    }
    else if (serialData == "mainLightsAuto") 
    {
      lightsAuto();
      sendSerialData("Do Main Lights Auto");
      
      return;
    }
    else if (checkFirstThree(serialData, "RGB") == true)
    {
      //default colour
      if((serialData[3] == 'D') && (serialData[4] == 'E') && (serialData[5] == 'F'))
      {
        DefaultColour();
        sendSerialData("Default colour");
        
        return;
      }
      else
      {
        //colour
        sendSerialData("Custom Colour");

        int r, g, b;
        String rStr = String(serialData[4]) + String(serialData[5]);
        String gStr = String(serialData[6]) + String(serialData[7]);  
        String bStr = String(serialData[8]) + String(serialData[9]);
        r = min(255, ((int)strtol(rStr.c_str(), NULL, 16) * 4));
        g = min(255, ((int)strtol(gStr.c_str(), NULL, 16) / 2));
        b = min(255, ((int)strtol(bStr.c_str(), NULL, 16) / 2));
        int diff = min(min(255-r, 255-g), 255-g);
        r += diff;
        g += diff;
        b += diff;
        ChangeColour(r, g, b);

        
        return;
      }
    }
    else if (checkFirstThree(serialData, "MBR") == true)
    {
      //BrightnessMainLight
      sendSerialData("Main Lights Brightness");
      String temp = "";
      for(int i = 3; i < serialData.length(); i++)
      {
        temp += serialData[i];
      }
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
      sendSerialData("Side Lights Brightness");
      
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
      sendSerialData("Warmth");
      
      ChangeWarmth(temp.toInt());
      return;
    }
    else if (checkFirstThree(serialData, "MLO") == true)
    {
      sendSerialData("Main Lights Override");
      
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
      sendSerialData("Bar Lights On/Off");
      
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
      sendSerialData("Main Lights On/Off");
      
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
      sendSerialData("Side Lights On/Off");
      
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
      sendSerialData("Ingredient Lights");
      

      clearAllIngredients();
      if((serialData.length() <= 3) || ((serialData[3] == 'C') && (serialData[4] == 'L') && (serialData[5] == 'R')))
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
    else
    {
      sendSerialData("!");
    }
    
}

bool commandStarted = false;
void loop() {
  
  
  while(Serial.available() > 0)
  {
    char inChar = (char)Serial.read();

    if(inChar == '>')
    {
      checkSerialData(serialData);
      serialData = "";
    }
    else
    {
      serialData += inChar;
    }
    
  }

  //while(Serial.available() > 0) 
  //{

  //  String serialData = Serial.readStringUntil('\n');
  //  sendSerialData(serialData);
  //  delay(100);

  //}

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
    colourChangeAlpha = min(255, colourChangeAlpha + 4);
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
  delay(5);
}
