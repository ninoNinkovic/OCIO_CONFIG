


import "utilities";
import "utilities-color";
import "PQ";

float aces_to_PQ_32f(float acesValue) 
{
  if (acesValue <= 0.0) return 0.0;
  
  float PQ = PQ10000_r(acesValue);
  
  return PQ;
}

// Display referred range: (Technicolor display referred files)
const float rangeMin=pow(2.0, -7.64);
const float rangeMax=pow(2.0, 13.3);

void main 
(
  input varying float rIn, 
  input varying float gIn, 
  input varying float bIn, 
  output varying float rOut,
  output varying float gOut,
  output varying float bOut,
  output varying float aOut 
)
{
  float aces[3] = {rIn, gIn, bIn};
 
  aces = clamp_f3( aces, rangeMin, rangeMax);
  
  aces[0] = (aces[0] - rangeMin)/(rangeMax-rangeMin);
  aces[1] = (aces[1] - rangeMin)/(rangeMax-rangeMin);
  aces[2] = (aces[2] - rangeMin)/(rangeMax-rangeMin);


  float acesLog32f[3];
  acesLog32f[0] = aces_to_PQ_32f( aces[0]);
  acesLog32f[1] = aces_to_PQ_32f( aces[1]);
  acesLog32f[2] = aces_to_PQ_32f( aces[2]);

  //print_f3(acesLog32f, aces);

  const float scalar = 1.0;
  rOut = acesLog32f[0] / scalar;
  gOut = acesLog32f[1] / scalar;
  bOut = acesLog32f[2] / scalar;
  aOut = 1.0;
}
