package examples.Mandelbrot;

import java.awt.image.BufferedImage;

import JyCSP.Alt;
import JyCSP.JavaCspChannel;
import JyCSP.Par;

public class Harness {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		int x = 320;
		int y = 240;
		MandelbrotDisplay md = new MandelbrotDisplay(x,y);
		BufferedImage bufimage = new BufferedImage(x, y,
				BufferedImage.TYPE_INT_RGB);
		
		Mandelbrot[] m = new Mandelbrot[320];
		JavaCspChannel[] chn = new JavaCspChannel[320];
		
		for(int i = 0; i<x;i++){
			chn[i] = new JavaCspChannel();
			m[i] = new Mandelbrot(x,y,i, chn[i]);
		}
		
		Par p = new Par(m);
		Alt a = new Alt(chn);
		p.start();
		while(a.hasNext()){
			Result r = (Result)a.select();
			bufimage.setRGB(r.getX(), 0, 1, r.getCol().length-1, r.getCol(), 0, 1);
			md.impnl.setImage(bufimage);
			md.setVisible(true);
			a.poison();
			}
		

	}

}
