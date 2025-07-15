export default (value, formatK = false) => {
  
    let formatted_value = value
    .toFixed(2)
    .replace(".", ",")
    .replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1.");

    // condições de saída (não precisa formatar)
    if (formatK) {
      if (formatted_value.length <= 9) { //ex: 99.999,00
        return formatted_value;
      }
    } else {
      if (formatted_value.length < 11) { //ex: 999.999,00
        return formatted_value;
      }
    }

    // 100.000,00
    let value_without_decimals = formatted_value.split(","); //remove decimais 100.000
    let unit = "";

    if (value_without_decimals[0]) {        
      value_without_decimals = value_without_decimals[0];   

      let split = value_without_decimals.split(".");  //[100, 000]

      if (split.length && split[0]) {   
        let digit = split[0];         //100

        if (formatK) {
          if (split.length <= 1) {
            return formatted_value;
          }
        } else {
          if (split.length <= 2) {
            return formatted_value;
          }
        }

        if (split.length == 2 && formatK) {
          unit = "K";
        } else if (split.length == 3) {
          unit = "M";
        } else if (split.length == 4) {
          unit = "B";
        }
        
        if (split[1]) {
          let decimal = split[1].substr(0, 2);
          if (parseInt(decimal) > 0) {
            digit = digit + "." + decimal;
          }
        }

        return `${digit} ${unit}`;
      } else {
        return formatted_value;
      }
    } else {
      return formatted_value;
    }
    
};
