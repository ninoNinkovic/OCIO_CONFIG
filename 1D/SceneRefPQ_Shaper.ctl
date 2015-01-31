


import "utilities";
import "utilities-color";
import "PQ";

float aces_to_PQ_32f(float acesValue) 
{
  if (acesValue <= 0.0) return 0.0;
  
  float PQ = PQ10000_r(acesValue);
  
  return PQ;
}

// range of LMT0.1.1 in v0.7.1
// 0.0000019180  -18.991965849
// 15.7761012587  3.97966881166
// [-18.991965849, 3.97966881166] 

// range of LMT 0.1.1 in V0.7.1
// 0.0000054932  -17.4739217499
// 16.2917402385  4.02606881166
// 
const float rangeMin=0.0000019180;
const float rangeMax=16.2917402385;

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

  //print_f3(acesLog32f);

  const float scalar = 1.0;
  rOut = acesLog32f[0] / scalar;
  gOut = acesLog32f[1] / scalar;
  bOut = acesLog32f[2] / scalar;
  aOut = 1.0;
}
