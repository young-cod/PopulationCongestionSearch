document.addEventListener("DOMContentLoaded", () => {
  // 계산기 로직 구현
  const display = document.querySelector(".calc-display");
  document.querySelectorAll(".calc-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const btnContent = btn.textContent;

      switch (btnContent) {
        case "C":
          display.value = "";
          break;
        case "=":
          try {
            // 수식 정리 및 계산
            const expression = display.value
              .replace(/×/g, "*")
              .replace(/÷/g, "/")
              .trim();
            if (!expression) return;
            display.value = math.evaluate(expression);
          } catch (error) {
            display.value = "Error";
          }
          break;
        case "±":
          if (display.value && !isNaN(display.value)) {
            display.value = (-parseFloat(display.value)).toString();
          }
          break;
        case "%":
          if (display.value && !isNaN(display.value)) {
            display.value = (parseFloat(display.value) / 100).toString();
          }
          break;
        default:
          display.value += btnContent;
      }
    });
  });

});

