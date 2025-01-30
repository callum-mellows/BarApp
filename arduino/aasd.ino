#include <FastLED.h>

#define NUM_LEDS 20
#define DATA_PIN 3

bool isFadingIn = false;
bool isFadingOut = false;
int currentBrightness = 1;

CRGB previousColour = CRGB::Black;
CRGB currentColour = CRGB::Black;
CRGB nextColour = CRGB::Black;
int colourChangeAlpha = 255;

CRGB leds[NUM_LEDS];

void setup() { 
  Serial.begin(15200);
  changeAllLEDs(CRGB::White);
  FastLED.addLeds<WS2811, DATA_PIN, RGB>(leds, NUM_LEDS);
}

void changeAllLEDs(CRGB newColour)
{
    for(int i = 0; i < NUM_LEDS; i++)
    {
      leds[i] = newColour;
    }
}

void StartFadeIn()
{
isFadingIn = true;
isFadingOut = false;
}

void StartFadeOut()
{
isFadingIn = false;
isFadingOut = true;
}

void ChangeColour(String newColourHex)
{
  int r, g, b;
  sscanf(&newColourHex[1], "%2x%2x%2x", &r, &g, &b);
  nextColour = CRGB(r, g, b);
  colourChangeAlpha = 0;
}


void loop() {

  String content = "";
  String character;

  String data = "";
      
  //while(Serial.available()) {
  //    character = Serial.readString();
  //    content.concat(character);
  //}
      
  if(Serial.available() > 0) {
    data = Serial.readStringUntil('\n');
    
  }

  if (data != "") {

    Serial.println(data);
    Serial.flush();

    if (data == "fadeIn") 
    {
      StartFadeIn();
    }
    else if (data == "fadeOut") 
    {
      StartFadeOut();
    }
    else if ((data[0] == 'R') && (data[1] == 'G') && (data[2] == 'B'))
    {
      String hexColour = String(data).substring(4);
      //String hexColour = data[4] + data[5] + data[6] + data[7] + data[8] + data[9];
      ChangeColour(hexColour);
    }



  }


  if(isFadingIn == true)
  {
    if(currentBrightness < 255)
    {
      currentBrightness++;
      return;
    }
  }
  if (isFadingOut == true)
  {
    if(currentBrightness > 0)
      {
        currentBrightness--;
        return;
      }
  }

  if(colourChangeAlpha < 255)
  {
    changeAllLEDs(nextColour);
    colourChangeAlpha++;
  }


  FastLED.setBrightness(currentBrightness);
  FastLED.show();
}
