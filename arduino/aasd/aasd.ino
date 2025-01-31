#include <FastLED.h>
#include <string.h>

#define NUM_LEDS 20
#define DATA_PIN 3

bool isFadingIn = false;
bool isFadingOut = false;
int currentBrightness = 0;
int previousBrightness = 128;
int nextBrightness = 128;
int brightnessAlpha = 255;
int maxBrightness = 128;

CRGB previousColour = CRGB::Black;
CRGB currentColour = CRGB::Black;
CRGB nextColour = CRGB::Black;
int colourChangeAlpha = 255;

CRGB defaultColour = CRGB::White;
ColorTemperature colourTemps[9] = {ColorTemperature::Candle, ColorTemperature::Tungsten40W, ColorTemperature::Tungsten100W, ColorTemperature::Halogen, ColorTemperature::CarbonArc, ColorTemperature::HighNoonSun, ColorTemperature::DirectSunlight, ColorTemperature::OvercastSky, ColorTemperature::ClearBlueSky};

CRGB leds[NUM_LEDS];

void setup() { 
  Serial.begin(15200);
  changeAllLEDs(defaultColour);
  previousColour = defaultColour;
  nextColour = defaultColour;
  FastLED.addLeds<WS2811, DATA_PIN, BRG>(leds, NUM_LEDS);
  FastLED.setMaxPowerInMilliWatts(12000);
  FastLED.setBrightness(0);
}

void changeAllLEDs(CRGB newColour)
{
    FastLED.clear();
    for(int i = 0; i < NUM_LEDS; i++)
    {
      leds[i] = newColour;
    }
}

void StartFadeIn()
{
  DefaultColour();
  isFadingIn = true;
  isFadingOut = false;
  brightnessAlpha = 0;
  previousBrightness = nextBrightness;
  nextBrightness = maxBrightness;
}

void StartFadeOut()
{
  DefaultColour();
  isFadingIn = false;
  isFadingOut = true;
  brightnessAlpha = 0;
  previousBrightness = nextBrightness;
  nextBrightness = 0;
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

void ChangeBrightness(int newBrightness)
{
  maxBrightness = newBrightness;
  previousBrightness = nextBrightness;
  nextBrightness = map(newBrightness, 0, 100, 0, 256);
  StartFadeIn();
}

void ChangeWarmth(int newWarmth)
{
  ColorTemperature temp = colourTemps[map(newWarmth, 0, 100, 8, 0)];
  defaultColour = CRGB(temp);
  DefaultColour();
}


void loop() {
  String serialData = "";
  if(Serial.available() > 0) {
    serialData = Serial.readStringUntil('\n');
  }

  if (serialData != "") {

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
    else if ((serialData[0] == 'R') && (serialData[1] == 'G') && (serialData[2] == 'B'))
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
    else if ((serialData[0] == 'B') && (serialData[1] == 'R') && (serialData[2] == 'I')) 
    {
      //Brightness
      String temp = "";
      for(int i = 3; i < serialData.length(); i++)
      {
        temp += serialData[i];
      }
      Serial.println(serialData);
      Serial.flush();
      ChangeBrightness(temp.toInt());
      
    }
    else if ((serialData[0] == 'W') && (serialData[1] == 'A') && (serialData[2] == 'R')) 
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
  }

  if(brightnessAlpha < 255)
  {
    currentBrightness = map(brightnessAlpha, 0, 254, previousBrightness, nextBrightness);
    brightnessAlpha++;
  }
  
  if(colourChangeAlpha < 255)
  {
    currentColour.r = map(colourChangeAlpha, 0, 254, previousColour.r, nextColour.r);
    currentColour.g = map(colourChangeAlpha, 0, 254, previousColour.g, nextColour.g);
    currentColour.b = map(colourChangeAlpha, 0, 254, previousColour.b, nextColour.b);

    changeAllLEDs(currentColour);
    colourChangeAlpha++;
  }


  FastLED.setBrightness(currentBrightness);
  FastLED.show();
  delay(5);
}
