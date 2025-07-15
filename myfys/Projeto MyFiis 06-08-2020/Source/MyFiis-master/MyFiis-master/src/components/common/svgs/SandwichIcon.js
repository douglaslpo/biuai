import * as React from "react"
import Svg, { Rect } from "react-native-svg"

function SvgComponent(props) {
    return (
        <Svg width={21} height={20} viewBox="0 0 21 20" fill="none" {...props}>
            <Rect
                x={0.667}
                y={8.75}
                width={20.33}
                height={2.5}
                rx={1.25}
                fill="#fff"
            />
            <Rect x={0.667} width={10.165} height={2.5} rx={1.25} fill="#fff" />
            <Rect
                x={10.832}
                y={17.5}
                width={10.165}
                height={2.5}
                rx={1.25}
                fill="#fff"
            />
        </Svg>
    )
}

export default SvgComponent
