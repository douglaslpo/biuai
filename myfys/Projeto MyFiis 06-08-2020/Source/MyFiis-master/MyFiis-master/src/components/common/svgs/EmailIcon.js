import * as React from "react";
import Svg, { Path } from "react-native-svg";

function EmailIcon(props) {
  return (
    <Svg width={15} height={14} viewBox="0 0 15 14" fill="none" {...props}>
      <Path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M1.364 0h12.272C14.39 0 15 .696 15 1.556v10.888c0 .86-.61 1.556-1.364 1.556H1.364C.61 14 0 13.304 0 12.444V1.556C0 .696.61 0 1.364 0zm0 5.147v7.297h12.272V5.148L7.5 8.648l-6.136-3.5zm0-1.739l6.136 3.5 6.136-3.5V1.557H1.364v1.852z"
        fill="#E0E0E0"
      />
    </Svg>
  );
}

export default EmailIcon;
