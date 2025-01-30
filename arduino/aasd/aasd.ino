#include <FastLED.h>
#include <string.h>

#define NUM_LEDS 20
#define DATA_PIN 3

bool isFadingIn = false;
bool isFadingOut = false;
int currentBrightness = 0;

CRGB previousColour = CRGB::Black;
CRGB currentColour = CRGB::Black;
CRGB nextColour = CRGB::Black;
int colourChangeAlpha = 255;

CRGB leds[NUM_LEDS];

void setup() { 
  Serial.begin(15200);
  changeAllLEDs(CRGB::White);
  previousColour = CRGB::White;
  nextColour = CRGB::White;
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
  ChangeColour(255, 255, 255);
  isFadingIn = true;
  isFadingOut = false;
}

void StartFadeOut()
{
  ChangeColour(255, 255, 255);
  isFadingIn = false;
  isFadingOut = true;
}

void ChangeColour(int r, int g, int b)
{
  previousColour = currentColour;
  nextColour = CRGB(r, g, b);
  colourChangeAlpha = 0;
}


void loop() {
  String serialData = "";
  if(Serial.available() > 0) {
    serialData = Serial.readStringUntil('\n');
  }

  if (serialData != "") {

    if (serialData == "fadeIn") 
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

  if(isFadingIn == true)
  {
    if(currentBrightness < 255)
    {
      currentBrightness++;
    }
  }
  else if (isFadingOut == true)
  {
    if(currentBrightness > 0)
      {
        currentBrightness--;
      }
  }
  
  if(colourChangeAlpha < 255)
  {
    currentColour.r = map(colourChangeAlpha, 0, 255, previousColour.r, nextColour.r);
    currentColour.g = map(colourChangeAlpha, 0, 255, previousColour.g, nextColour.g);
    currentColour.b = map(colourChangeAlpha, 0, 255, previousColour.b, nextColour.b);

    changeAllLEDs(currentColour);
    colourChangeAlpha++;
  }


  FastLED.setBrightness(currentBrightness/2);
  FastLED.show();
  delay(5);
}
