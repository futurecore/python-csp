
public class Harness {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		float[][] h = new float[1000][1000];
		float[][] id = new float[1000][1000];
		for(int i = 0; i<1000;i ++){
			for(int j = 0; j<1000;j++){
				h[i][j] = (float) Math.random();
				if(i == j){
					id[i][j] = 1;
				} else {
					id[i][j] = 0;
				}
			}
		}

		Matrix a = new Matrix(h);
		Matrix b = new Matrix(id);
		//b.print();
		System.out.println("-----------------------------------------------------------------");
		try {
			long t0 = System.currentTimeMillis();
			Matrix f = b.ParMultiplyMatrix(b,10);
			//f.print();
			long t1 = System.currentTimeMillis();
			System.out.println("Time take for Parallel: " +  (t1-t0));
			
			t0 = System.currentTimeMillis();
			Matrix g = b.MultiplyMatrix(b);
			//g.print();
			t1 = System.currentTimeMillis();
			System.out.println("Time take for Seq: " +  (t1-t0));
		} catch (Exception e) {
			
			
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}

}
