(function () {
  var canvas = document.querySelector('#canvas');
  var ctx = canvas.getContext('2d');

  canvas.style.position = 'absolute';
  canvas.style.top = '0';
  canvas.style.left = '0';

  resize();
  window.onresize = resize;
  function resize() {
    canvas.width = document.querySelector('body').offsetWidth;
    canvas.height = document.querySelector('body').offsetHeight;
  }

  var RAF = (function () {
    return window.requestAnimationFrame || window.mozRequestAnimationFrame || window.msRequestAnimationFrame ||
      window.webkitRequestAnimationFrame || window.oRequestAnimationFrame ||
      function (callback) {
        window.setTimeout(callback, 1000 / 60);
      };
  })();
  // Get mouse position
  var pointer = {x: null, y: null, max: 20000};
  canvas.onmousemove = function (e) {
    e = e || window.event;
    pointer.x = e.clientX;
    pointer.y = e.clientY;
  };
  canvas.onmouseout = function () {
    pointer.x = null;
    pointer.y = null;
  };
  // Dots
  // x, y: Position; xa, ya: Acceleration; max: max line length
  var dots = [], dotsNum = 100;
  for (var i = 0; i < dotsNum; i++) {
    var x = Math.random() * canvas.width;
    var y = Math.random() * canvas.height;
    var xa = Math.random() * 2 - 1;
    var ya = Math.random() * 2 - 1;
    dots.push({
      x: x,
      y: y,
      xa: xa,
      ya: ya,
      max: 6000
    })
  }
  // Gradient
  var gradientColor = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
  gradientColor.addColorStop(0, '#7474BF');
  gradientColor.addColorStop(1, '#348AC7');
  // Delay some time to avoid rendering bug
  setTimeout(function () {
    animate();
  }, 100);
  // Frame
  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = gradientColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    // Dots + Cursor Position
    var DaC = [pointer].concat(dots);
    dots.forEach(function (dot) {
      // Move
      dot.x += dot.xa;
      dot.y += dot.ya;
      // Bounce
      dot.xa *= (dot.x > canvas.width || dot.x < 0) ? -1 : 1;
      dot.ya *= (dot.y > canvas.height || dot.y < 0) ? -1 : 1;
      // Render
      ctx.fillRect(dot.x - 0.5, dot.y - 0.5, 1, 1);
      // Calculate distance and draw lines
      for (var i = 0; i < DaC.length; i++) {
        var d = DaC[i];
        if (dot === d || d.x === null || d.y === null)
          continue;
        var xc = dot.x - d.x;
        var yc = dot.y - d.y;
        // Distance
        var dis = xc * xc + yc * yc;
        // Draw a line when distance < max
        if (dis < d.max) {
          // Gather to the cursor
          if (d === pointer && dis > (d.max / 2)) {
            dot.x -= xc * 0.03;
            dot.y -= yc * 0.03;
          }
          // Ratio of distance
          var ratio = (d.max - dis) / d.max;
          // Draw a line
          ctx.beginPath();
          ctx.lineWidth = ratio / 2;
          ctx.strokeStyle = 'rgba(255, 255, 255,' + (ratio + 0.2) + ')';
          ctx.moveTo(dot.x, dot.y);
          ctx.lineTo(d.x, d.y);
          ctx.stroke();
        }
      }
      // Delete this dot
      DaC.splice(DaC.indexOf(dot), 1);
    });
    // Animate it
    RAF(animate);
  }
}());
