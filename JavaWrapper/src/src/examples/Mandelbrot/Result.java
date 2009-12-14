package examples.Mandelbrot;
import java.io.Serializable;



public class Result implements Serializable {

	private int x;
	private int[] col;

	public Result(int x, int[] col) {
		super();
		this.x = x;
		this.col = col;
	}

	public int getX() {
		return x;
	}

	public void setX(int x) {
		this.x = x;
	}

	public int[] getCol() {
		return col;
	}

	public void setCol(int[] col) {
		this.col = col;
	}

}
