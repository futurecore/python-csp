package examples.Mandelbrot;

import java.awt.Graphics;
import java.awt.Image;
import java.awt.Panel;
import java.awt.image.BufferedImage;


public class ImagePanel extends Panel {
	private Image myimg = null;

	public ImagePanel() {
		setLayout(null);
		setSize(500, 500);
		this.setMyimg(new BufferedImage(500,500,BufferedImage.TYPE_INT_RGB));
	}
	
	public ImagePanel(int x, int y) {
		setLayout(null);
		setSize(x, y);
		this.setMyimg(new BufferedImage(x,y,BufferedImage.TYPE_INT_RGB));
	}

	public void setImage(Image img) {
		this.setMyimg(img);
		repaint();
	}

	public void paint(Graphics g) {
		if (getMyimg() != null) {
			g.drawImage(getMyimg(), 0, 0, this);
		}
	}
	
	public BufferedImage getCompatible(){
		return new BufferedImage(this.getMyimg().getWidth(null),this.getMyimg().getHeight(null),BufferedImage.TYPE_INT_RGB);
	}

	/**
	 * @return the myimg
	 */
	public Image getImage() {
		return getMyimg();
	}

	public void setMyimg(Image myimg) {
		this.myimg = myimg;
	}

	public Image getMyimg() {
		return myimg;
	}
}