import * as React from "react";
import Svg, { Path } from "react-native-svg";

function KeyIcon(props) {
  return (
    <Svg width={15} height={23} viewBox="0 0 15 23" fill="none" {...props}>
      <Path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M4.25 12.958a4.958 4.958 0 114.958 4.959H7.792v1.416H6.375v1.417H4.958v1.417H0v-3.835l4.355-4.355a4.977 4.977 0 01-.105-1.019zM6.375 16.5h2.833a3.542 3.542 0 10-3.39-2.513l.123.407-4.524 4.524v1.832h2.125v-1.417h1.416v-1.416h1.417V16.5zm1.417-3.542a1.417 1.417 0 102.833 0 1.417 1.417 0 00-2.833 0z"
        fill="#E0E0E0"
      />
    </Svg>
  );
}

export default KeyIcon;
