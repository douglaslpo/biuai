import * as React from "react";
import Svg, { Path, Defs, LinearGradient, Stop } from "react-native-svg";

function ArrowButton(props) {
  return (
    <Svg width={22} height={24} viewBox="0 0 22 24" fill="none" {...props}>
      <Path
        d="M21.061 13.061a1.502 1.502 0 000-2.122l-9.546-9.546a1.502 1.502 0 00-2.122 0 1.502 1.502 0 000 2.122L17.879 12l-8.486 8.485a1.502 1.502 0 000 2.122 1.502 1.502 0 002.122 0l9.546-9.546zM0 13.5h20v-3H0v3z"
        fill="url(#prefix__paint0_linear)"
      />
      <Defs>
        <LinearGradient
          id="prefix__paint0_linear"
          x1={-10.75}
          y1={12}
          x2={11.334}
          y2={33.492}
          gradientUnits="userSpaceOnUse"
        >
          <Stop stopColor="#26BFBD" />
          <Stop offset={1} stopColor="#00E1B5" />
        </LinearGradient>
      </Defs>
    </Svg>
  );
}

export default ArrowButton;
