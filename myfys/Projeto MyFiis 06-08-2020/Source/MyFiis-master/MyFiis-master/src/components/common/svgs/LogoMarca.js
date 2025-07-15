import React from "react";
import Svg, { G, Path, Defs, LinearGradient, Stop } from "react-native-svg";
/* SVGR has dropped some elements not supported by react-native-svg: filter */

const LogoMarca = (props) => (
  <Svg width={68} height={102} viewBox="0 0 68 102" fill="none" {...props}>
    <G filter="url(#filter0_d)">
      <Path
        d="M36.308 0L64 11.832v81.887H36.308V0z"
        fill="url(#paint0_linear)"
      />
      <Path
        d="M31.508 40.078L4 49.669V94h27.508V40.078z"
        fill="url(#paint1_linear)"
      />
      <Path
        d="M16.092 69.16h-4.458v-4.014h4.458v4.014zM22.331 69.16h-4.457v-4.014h4.457v4.014zM16.092 74.415h-4.458V70.4h4.458v4.015zM22.331 74.415h-4.457V70.4h4.457v4.015zM49.72 24.417h-4.458v-4.014h4.457v4.014zM55.959 24.417H51.5v-4.014h4.458v4.014zM49.72 29.672h-4.458v-4.015h4.457v4.015zM55.959 29.672H51.5v-4.015h4.458v4.015zM31.508 50.28l13.754 6.506V94H31.508V50.28z"
        fill="#fff"
      />
    </G>
    <Defs>
      <LinearGradient
        id="paint0_linear"
        x1={36.3082}
        y1={46.2347}
        x2={64}
        y2={46.2347}
        gradientUnits="userSpaceOnUse"
      >
        <Stop offset={0.53125} stopColor="#29B5A4" />
      </LinearGradient>
      <LinearGradient
        id="paint1_linear"
        x1={17.754}
        y1={94}
        x2={17.754}
        y2={40.0775}
        gradientUnits="userSpaceOnUse"
      >
        <Stop stopColor="#29B5A4" />
        <Stop offset={1} stopColor="#29B5A4" />
      </LinearGradient>
    </Defs>
  </Svg>
);

export default LogoMarca;
