package examples.Matrix;

public class Harness {

	/**
	 * @param args
	 * @throws Exception 
	 */
	public static void main(String[] args) throws Exception {
		Matrix m = Matrix.createIdentity(100);
		Matrix n = Matrix.createIdentity(100);
		
		long t0 = System.currentTimeMillis();
		m.MultiplyMatrix(n);
		long t1 = System.currentTimeMillis();
		
		System.out.println("Time taken for Sequential : " + (t1-t0));
		
		t0 = System.currentTimeMillis();
		m.ParMultiplyMatrix(n, 100);
		t1 = System.currentTimeMillis();
		System.out.println("Time taken for Parallel: " + (t1-t0));
		

	}

}
