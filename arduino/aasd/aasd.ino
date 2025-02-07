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

int strip1currentBrightness[NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT];
int strip2currentBrightness[NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT];
int strip1nextBrightness[NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT];
int strip2nextBrightness[NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT];

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
  Serial.begin(15200);
  FastLED.setBrightness(0);
  
  previousColour = defaultColour;
  nextColour = defaultColour;
  FastLED.addLeds<WS2811, PIN_BAR_LIGHTS, BRG>(barLeds, NUM_SIDE_LIGHTS);
  FastLED.addLeds<WS2811, PIN_SCREEN_LIGHTS, BRG>(screenLeds, NUM_SCREEN_LIGHTS);
  
  FastLED.addLeds<WS2811, PIN_INGREDIENT_STRIP_1, GRB>(ingredientLeds1, NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT);
  FastLED.addLeds<WS2811, PIN_INGREDIENT_STRIP_2, GRB>(ingredientLeds2, NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT);
  
  for(int i = 0; i < NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT; i++)
  {
      strip1currentBrightness[i] = 0;
      strip2currentBrightness[i] = 0;
  }
  clearAllIngredients();

  changeAllLEDs(defaultColour);
  FastLED.setMaxPowerInMilliWatts(12000);
  

  pinMode(PIN_MAIN_LIGHT_1, OUTPUT);
  pinMode(PIN_MAIN_LIGHT_2, OUTPUT);
  pinMode(PIN_BAR_LIGHTS, OUTPUT);
  pinMode(PIN_SCREEN_LIGHTS, OUTPUT);
  pinMode(PIN_INGREDIENT_STRIP_1, OUTPUT);
  pinMode(PIN_INGREDIENT_STRIP_2, OUTPUT);
}

void clearAllIngredients()
{
  for(int i = 0; i < NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT; i++)
  {
      strip1nextBrightness[i] = 0;
      strip2nextBrightness[i] = 0;
  }
}

void setIngredientOn(int strip, int index)
{
  if(strip == 0)
  {
    for(int j = 0; j < NUM_LEDS_PER_LIGHT; j++)
    {
      strip1nextBrightness[(index*NUM_LEDS_PER_LIGHT)+j] = 255;
    }
  }
  else if(strip == 1)
  {
    for(int j = 0; j < NUM_LEDS_PER_LIGHT; j++)
    {
      strip2nextBrightness[(index*NUM_LEDS_PER_LIGHT)+j] = 255;
    }
  }
}

/*
void setIngredientLedBrightness(int strip, int index, int brightness)
{
  if(strip == 0)
  {
    for(int j = 0; j < NUM_LEDS_PER_LIGHT; j++)
    {
      ingredientLeds1[(index*NUM_LEDS_PER_LIGHT)+j] = CRGB(brightness, brightness, brightness);
    }
  }
  else if(strip == 1)
  {
    for(int j = 0; j < NUM_LEDS_PER_LIGHT; j++)
    {
      ingredientLeds2[(index*NUM_LEDS_PER_LIGHT)+j] = CRGB(brightness, brightness, brightness);
    }
  }
}
*/

void changeAllLEDs(CRGB newColour)
{
    FastLED.clear();
    for(int i = 0; i < NUM_SIDE_LIGHTS; i++)
    {
      if(barLightsOn == true)
      {
        barLeds[i] = newColour;
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
        screenLeds[i] = newColour;
      }
      else
      {
        screenLeds[i] = CRGB::Black;
      }
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

void checkSerialData(String serialData)
{
  Serial.println("In: " + serialData);

    if (serialData == "asd")
    {
      Serial.println("garbage!");
      Serial.flush();
      return;
    }
    else if (serialData == "fadeIn") 
    {
      StartFadeIn();
      Serial.println(serialData);
      Serial.flush();
      return;
    }
    else if (serialData == "fadeOut") 
    {
      StartFadeOut();
      Serial.println(serialData);
      Serial.flush();
      return;
    }
    else if (serialData == "mainLightsOn") 
    {
      lightsOn();
      Serial.println(serialData);
      Serial.flush();
      return;
    }
    else if (serialData == "mainLightsOff") 
    {
      lightsOff();
      Serial.println(serialData);
      Serial.flush();
      return;
    }
    else if (serialData == "mainLightsAuto") 
    {
      lightsAuto();
      Serial.println(serialData);
      Serial.flush();
      return;
    }
    else if (checkFirstThree(serialData, "RGB") == true)
    {
      //default colour
      if((serialData[3] == 'D') && (serialData[4] == 'E') && (serialData[5] == 'F'))
      {
        DefaultColour();
        Serial.println(serialData);
        Serial.flush();
        return;
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
      Serial.println(serialData);
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
      Serial.println(serialData);
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
      Serial.println(serialData);
      Serial.flush();
      ChangeWarmth(temp.toInt());
      return;
    }
    else if (checkFirstThree(serialData, "MLO") == true)
    {
      Serial.println(serialData);
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
      Serial.println(serialData);
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
      Serial.println(serialData);
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
      Serial.println(serialData);
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
    /*
    else if (checkFirstThree(serialData, "ING") == true)
    {
      Serial.println(serialData);
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
    */
}

void loop() {
  String serialData = "";
  if(Serial.available() > 0) {
    String sData = Serial.readStringUntil('\n');
    checkSerialData(sData);
  }

  if(BrightnessSideLightAlpha < 255)
  {
    currentBrightnessSideLight = map(BrightnessSideLightAlpha, 0, 254, previousBrightnessSideLight, nextBrightnessSideLight);
    BrightnessSideLightAlpha++;
    FastLED.setBrightness(currentBrightnessSideLight);
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

  
  for(int i = 0; i < NUM_INGREDIENT_LIGHTS_PER_STRIP * NUM_LEDS_PER_LIGHT; i++)
  {
    if(strip1nextBrightness[i] > strip1currentBrightness[i])
    {
      strip1currentBrightness[i]++;
    }
    else if(strip1nextBrightness[i] < strip1currentBrightness[i])
    {
      strip1currentBrightness[i]--;
    }
    //ingredientLeds1[i] = CRGB(strip1currentBrightness[i], strip1currentBrightness[i], strip1currentBrightness[i]);
    ingredientLeds1[i] = CRGB::Red;
    //setIngredientLedBrightness(0, i, strip1currentBrightness[i]);
    /*
    if(strip2nextBrightness[i] > strip2currentBrightness[i])
    {
      strip2currentBrightness[i]++;
    }
    else if(strip2nextBrightness[i] < strip2currentBrightness[i])
    {
      strip2currentBrightness[i]--;
    }
    //setIngredientLedBrightness(1, i, strip2currentBrightness[i]);
  */
  }
  


  
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
