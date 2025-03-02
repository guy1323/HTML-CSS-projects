const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const width = (canvas.width = window.innerWidth);
const height = (canvas.height = window.innerHeight);
const squareSize = 0.5;
const squareColor = "black";
const primeColor = "white";

var pos = {
  x: width / 2,
  y: height / 2,
};
var number = {
  limit: 1,
  num: 1,
  rotation: 3,
};
const primeArr = [];

function setup() {
  ctx.fillStyle = squareColor;
  ctx.strokeStyle = "white";

  ctx.lineWidth = 2;
  ctx.fillRect(pos.x, pos.y, squareSize, squareSize);
  number.num++;
  draw();
}

function draw() {
  for (let i = 0; i < 2; i++) {
    for (let j = 0; j < number.limit; j++) {
      checkPrime();
      printSquare(number.rotation);
      number.num++;
    }
    //turn
    number.rotation++;
  }
  number.limit++;
  if (pos.x < 0) {
    console.log("Finished");
    clearInterval(interval);
  }
}

function printSquare(rotation) {
  //print number
  switch (rotation % 4) {
    // /|\(up)
    case 0:
      ctx.fillRect(pos.x, pos.y, squareSize, squareSize);
      pos.y -= squareSize;
      break;
    //<--(left)
    case 1:
      ctx.fillRect(pos.x, pos.y, squareSize, squareSize);
      pos.x -= squareSize;
      break;
    //\|/(down)
    case 2:
      ctx.fillRect(pos.x, pos.y, squareSize, squareSize);
      pos.y += squareSize;
      break;
    //-->(right)
    case 3:
      ctx.fillRect(pos.x, pos.y, squareSize, squareSize);
      pos.x += squareSize;
      break;
  }
}
function checkPrime() {
  for (let i = 0; i < primeArr.length; i++) {
    if (number.num % primeArr[i] === 0) {
      ctx.fillStyle = squareColor;
      return false;
    }
  }
  primeArr.push(number.num);
  ctx.fillStyle = primeColor;
  return true;
}

setup();
const interval = setInterval(draw, 0);
