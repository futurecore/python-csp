package examples.Mandelbrot;
import java.awt.BorderLayout;
import java.awt.FlowLayout;

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

}
