import java.awt.BorderLayout;
import java.awt.Graphics;
import java.awt.Image;
import java.awt.Panel;
import java.awt.Color;
import java.awt.image.BufferedImage;

import javax.swing.*;


/**
* This code was edited or generated using CloudGarden's Jigloo
* SWT/Swing GUI Builder, which is free for non-commercial
* use. If Jigloo is being used commercially (ie, by a corporation,
* company or business for any purpose whatever) then you
* should purchase a license for each developer using Jigloo.
* Please visit www.cloudgarden.com for details.
* Use of Jigloo implies acceptance of these licensing terms.
* A COMMERCIAL LICENSE HAS NOT BEEN PURCHASED FOR
* THIS MACHINE, SO JIGLOO OR THIS CODE CANNOT BE USED
* LEGALLY FOR ANY CORPORATE OR COMMERCIAL PURPOSE.
*/
public class MandelbrotDisplay extends javax.swing.JFrame {
	private JPanel jPanel1;
	private JPanel jPanel2;
	private JPanel jPanel6;
	private JPanel jPanel5;
	private JPanel jPanel4;
	private JPanel jPanel3;
	
	public ImagePanel impnl;

	/**
	* Auto-generated main method to display this JFrame
	*/
	public static void main(String[] args) {
		SwingUtilities.invokeLater(new Runnable() {
			public void run() {
				MandelbrotDisplay inst = new MandelbrotDisplay(340,240);
				inst.setLocationRelativeTo(null);
				inst.setVisible(true);
			}
		});
	}
	
	public MandelbrotDisplay(int x, int y) {
		super();
		this.impnl = new ImagePanel(x,y);
		initGUI();
	}
	
	private void initGUI() {
		try {
			{
				this.setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
			}
			{
				jPanel1 = new JPanel();
				BorderLayout jPanel1Layout = new BorderLayout();
				jPanel1.setLayout(jPanel1Layout);
				getContentPane().add(jPanel1, BorderLayout.CENTER);
				{
					jPanel6 = new JPanel();
					jPanel1.add(jPanel6, BorderLayout.SOUTH);
					jPanel6.setPreferredSize(new java.awt.Dimension(732, 53));
				}
				{
					jPanel5 = new JPanel();
					jPanel1.add(jPanel5, BorderLayout.EAST);
					jPanel5.setPreferredSize(new java.awt.Dimension(72, 360));
				}
				{
					jPanel4 = new JPanel();
					jPanel1.add(jPanel4, BorderLayout.WEST);
					jPanel4.setPreferredSize(new java.awt.Dimension(55, 360));
				}
				{
					jPanel3 = new JPanel();
					jPanel1.add(jPanel3, BorderLayout.NORTH);
					jPanel3.setPreferredSize(new java.awt.Dimension(732, 48));
				}
				{
					jPanel2 = new JPanel();
					jPanel2.add(this.impnl);
					jPanel1.add(jPanel2, BorderLayout.CENTER);
				}
			}
			pack();
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		
	}
	
	public void setColorArray(int x, int[][] colors){
		int[] p = new int[colors.length];
		for(int i = 0; i<colors.length;i++){
			p[i] = new Color(colors[i][0], colors[i][1], colors[i][2]).getRGB();
		}
		this.impnl.setArray(x,p);
	}
	public void toggleVis(){
		this.setVisible(!this.isVisible());
	}

	public class ImagePanel extends Panel {
		private BufferedImage myimg = null;

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

		public void setImage(BufferedImage img) {
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

		public void setMyimg(BufferedImage myimg) {
			this.myimg = myimg;
		}

		public Image getMyimg() {
			return myimg;
		}
		
		public void setArray(int x,int[] colors){

			this.myimg.setRGB(x, 0, 1, this.myimg.getHeight(), colors, 0, 1);
			repaint();
			
		}
	}
}
