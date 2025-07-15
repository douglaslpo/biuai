import * as React from "react";
import Svg, { G, Path, Defs } from "react-native-svg";
/* SVGR has dropped some elements not supported by react-native-svg: filter */

function LoginBackground(props) {
  return (
    <Svg width={284} height={362} viewBox="0 0 284 362" fill="none" {...props}>
      <G filter="url(#prefix__filter0_d)">
        <Path
          d="M4 43.293C4 19.383 22.837 0 46.073 0h191.854C261.163 0 280 19.383 280 43.293V310.69c0 27.653-24.851 48.218-51.1 42.285L37.047 309.611C17.749 305.25 4 287.657 4 267.327V43.293z"
          fill="#fff"
        />
      </G>
      <Defs></Defs>
    </Svg>
  );
}

export default LoginBackground;
