package examples.Mandelbrot;
import java.awt.Color;
import java.awt.image.BufferedImage;

import JyCSP.JavaCspChannel;
import JyCSP.JavaCspProcess;
 
public class Mandelbrot extends JavaCspProcess {

	private int MAXITER = 100;
	private double acorn= -2.0;
	private double bcorn= -1.250;
	private int col;
	private int height;
	private int width;
	private JavaCspChannel chn;

	public Mandelbrot(int width, int height,int collumn, JavaCspChannel c) {
		super();	
		this.col = collumn;
		this.height = height;
		this.width = width;
		this.chn = c;
	}
	
	public void target(){
		this.makeCollumn(this.col);
	}

	public Color getColor(double mag, int cmin, int cmax) {
		assert cmin != cmax;
		float a = (float) ((mag - cmin) / (cmax - cmin));

		int blue = (int) Math.min((Math.max((4 * (0.75 - a)), 0.0)), 1.0);

		int red = (int) Math.min((Math.max((4 * (a - 0.25)), 0.0)), 1.0);

		int green = (int) Math.min(
				(Math.max((4 * Math.abs(a - 0.5) - 1.0), 0)), 1.0);

		return new Color(255 * red, 255 * green, 255 * blue);
	}

	public void makeCollumn(int x) {
		int[] collumn = new int[this.height];
		for(int y = 0; y<this.height;y++){
			Color color = new Color(0,0,0);
			Complex z = new Complex(0,0);
			Complex c = new Complex(this.acorn + x*2.5/this.width,
												this.bcorn + y*2.5/this.height);
			
			for(int i = 0; i<this.MAXITER; i++){
				z = new Complex(Math.pow(z.real(), 2)-Math.pow(z.imag(),2) + c.real(),
													2*z.real()*z.imag() + c.imag());
				
				if(Math.pow(z.mod(),2) > 4){
					break;
				}
				
				if(i == this.MAXITER -1){
					color = Color.BLACK;
				} else {
					color = this.getColor(getNu(z,i), 0, this.MAXITER);
				}
				
				collumn[y] = color.getRGB();
			}
			
		}
		Result r = new Result(x,collumn);
		this.chn.write(r);
	}

	private double getNu(Complex zz, int n) {
		// nu = lambda zz, n: n + 1 - math.log(math.log(abs(zz)))/math.log(2)
		return n + 1 - Math.log(Math.log(zz.mod()) / Math.log(2));
	}
}
