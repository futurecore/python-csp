

import java.text.DecimalFormat;
import java.util.concurrent.Semaphore;

public class Matrix
{


	private boolean DEBUG = false;

	private boolean INFO = false;

	private int iDF = 0;
	
	private float[][] matrix;

	public Matrix(Matrix m){
		this.matrix = m.getMatrix();
	}
	public Matrix(int size) {
		matrix = new float[size][size];
		}

	public Matrix(int sizeX,int sizeY) {
		matrix = new float[sizeY][sizeX];
		}

	public Matrix(float[][] m) {
		matrix = new float[m.length][m[0].length];
		matrix = m;
		}

	public void SetMatrix(float[][] m) {
		if(m.length==matrix.length && m[0].length==matrix[0].length)
		{
			this.matrix = m;
		}
	}

	public float[][] getMatrix() {
		return this.matrix;
	}
	
	public void print()
		{
			for(int i = 0; i<matrix.length; i++) 
			{
					System.out.print("{");
				for(int j = 0; j<matrix[0].length; j++) 
				{
					if(j<matrix[0].length-1)
					{
					System.out.print(" " + matrix[i][j] +",");
					}
					else {
						System.out.print(" " + matrix[i][j]);	
					}
					
				}
				System.out.println(" }");
				
			}
				
			
		}
	
	public void printformatted1(String Pattern)
	{
		DecimalFormat Formatter = new DecimalFormat(Pattern);
		

		for(int i = 0; i<matrix.length; i++) 
		{
				System.out.print("{");
			for(int j = 0; j<matrix[0].length; j++) 
			{
				if(j<matrix[0].length-1)
				{
				System.out.print(" " + Formatter.format(matrix[i][j]) +",");
				}
				else {
					System.out.print(" " + Formatter.format(matrix[i][j]));	
				}
				
			}
			System.out.println(" }");
			
		}
			
		
	}
	

	 public Matrix ParMultiplyMatrix(Matrix Mb,int gran) throws Exception {
		float[][] b = Mb.getMatrix();
		float[][] a = this.matrix;
		if(a[0].length != b.length)
			throw new Exception("Matrices incompatible for multiplication");
		float matrix[][] = new float[a.length][b[0].length];

		for (int i = 0; i < a.length; i = i + gran)
			for (int j = 0; j < b[i].length; j = j + gran)
				matrix[i][j] = 0;

		//cycle through answer matrix
		Matrix res = new Matrix(matrix);
		Semaphore s = new Semaphore(matrix.length);
		for(int i = 0; i < matrix.length/gran; i++){
			for(int j = 0; j < matrix[0].length/gran; j++){
				//matrix[i][j] = calculateRowColumnProduct(a,i,b,j);
				Thread f = new RCProduct(a,i*gran,b,j*gran,res,s,gran,gran); 
				f.start();
			}
		}
		s.acquire(matrix.length);
		return new Matrix(matrix);
	}
	 
	 public Matrix MultiplyMatrix(Matrix Mb) throws Exception {
			float[][] b = Mb.getMatrix();
			float[][] a = this.matrix;
			if(a[0].length != b.length)
				throw new Exception("Matrices incompatible for multiplication");
			float matrix[][] = new float[a.length][b[0].length];

			for (int i = 0; i < a.length; i++)
				for (int j = 0; j < b[i].length; j++)
					matrix[i][j] = 0;

			//cycle through answer matrix
			for(int i = 0; i < matrix.length; i++){
				for(int j = 0; j < matrix[i].length; j++){
					matrix[i][j] = calculateRowColumnProduct(a,i,b,j);
					
				}
			}
			
			return new Matrix(matrix);
		}

	public float calculateRowColumnProduct(float[][] A, int row, float[][] B, int col){
		float product = 0;
		for(int i = 0; i < A[row].length; i++)
			product +=A[row][i]*B[i][col];
		return product;
	}
	// --------------------------------------------------------------
	
	public float[][] Transpose() {
		float[][] a = this.matrix;
		
		if (INFO) {
			System.out.println("Performing Transpose...");
		}
		
		float m[][] = new float[a[0].length][a.length];

		for (int i = 0; i < a.length; i++)
			for (int j = 0; j < a[i].length; j++)
				m[j][i] = a[i][j];
		return m;
	}
	
	private float[][] Transpose(float[][] a) {
		
		
		if (INFO) {
			System.out.println("Performing Transpose...");
		}
		
		float m[][] = new float[a[0].length][a.length];

		for (int i = 0; i < a.length; i++)
			for (int j = 0; j < a[i].length; j++)
				m[j][i] = a[i][j];
		return m;
	}

	// --------------------------------------------------------------

	public Matrix Inverse() throws Exception {
		float[][] a = this.matrix;
		// Formula used to Calculate Inverse:
		// inv(A) = 1/det(A) * adj(A)
		if (INFO) {
			System.out.println("Performing Inverse...");
		}
		int tms = a.length;

		float m[][] = new float[tms][tms];
		float mm[][] = Adjoint(a);

		float det = Determinant(a);
		float dd = 0;

		if (det == 0) {
			
			if (INFO) {
				System.out.println("Determinant Equals 0, Not Invertible.");
			}
		} else {
			dd = 1 / det;
		}

		for (int i = 0; i < tms; i++)
			for (int j = 0; j < tms; j++) {
				m[i][j] = dd * mm[i][j];
			}

		return new Matrix(m);
	}

	// --------------------------------------------------------------

	public float[][] Adjoint() throws Exception {
		float[][] a = this.matrix;
		
		if (INFO) {
			System.out.println("Performing Adjoint...");
		}
		int tms = a.length;

		float m[][] = new float[tms][tms];

		int ii, jj, ia, ja;
		float det;

		for (int i = 0; i < tms; i++)
			for (int j = 0; j < tms; j++) {
				ia = ja = 0;

				float ap[][] = new float[tms - 1][tms - 1];

				for (ii = 0; ii < tms; ii++) {
					for (jj = 0; jj < tms; jj++) {

						if ((ii != i) && (jj != j)) {
							ap[ia][ja] = a[ii][jj];
							ja++;
						}

					}
					if ((ii != i) && (jj != j)) {
						ia++;
					}
					ja = 0;
				}

				det = Determinant(ap);
				m[i][j] = (float) Math.pow(-1, i + j) * det;
			}

		m = Transpose(m);

		return m;
	}



	private float[][] Adjoint(float[][] a) throws Exception {
		
		
		if (INFO) {
			System.out.println("Performing Adjoint...");
		}
		int tms = a.length;

		float m[][] = new float[tms][tms];

		int ii, jj, ia, ja;
		float det;

		for (int i = 0; i < tms; i++)
			for (int j = 0; j < tms; j++) {
				ia = ja = 0;

				float ap[][] = new float[tms - 1][tms - 1];

				for (ii = 0; ii < tms; ii++) {
					for (jj = 0; jj < tms; jj++) {

						if ((ii != i) && (jj != j)) {
							ap[ia][ja] = a[ii][jj];
							ja++;
						}

					}
					if ((ii != i) && (jj != j)) {
						ia++;
					}
					ja = 0;
				}

				det = Determinant(ap);
				m[i][j] = (float) Math.pow(-1, i + j) * det;
			}

		m = Transpose(m);

		return m;
	}

	// --------------------------------------------------------------

	public float[][] UpperTriangle() {
		float[][] m = this.matrix;
		
		if (INFO) {
			System.out.println("Converting to Upper Triangle...");
		}

		float f1 = 0;
		float temp = 0;
		int tms = m.length; // get This Matrix Size (could be smaller than
							// global)
		int v = 1;

		iDF = 1;

		for (int col = 0; col < tms - 1; col++) {
			for (int row = col + 1; row < tms; row++) {
				v = 1;

				outahere: while (m[col][col] == 0) // check if 0 in diagonal
				{ // if so switch until not
					if (col + v >= tms) // check if switched all rows
					{
						iDF = 0;
						break outahere;
					} else {
						for (int c = 0; c < tms; c++) {
							temp = m[col][c];
							m[col][c] = m[col + v][c]; // switch rows
							m[col + v][c] = temp;
						}
						v++; // count row switchs
						iDF = iDF * -1; // each switch changes determinant
										// factor
					}
				}

				if (m[col][col] != 0) {
					if (DEBUG) {
						System.out.println("tms = " + tms + "   col = " + col
								+ "   row = " + row);
					}

					try {
						f1 = (-1) * m[row][col] / m[col][col];
						for (int i = col; i < tms; i++) {
							m[row][i] = f1 * m[col][i] + m[row][i];
						}
					} catch (Exception e) {
						System.out.println("Still Here!!!");
					}

				}

			}
		}

		return m;
	}

	private float[][] UpperTriangle(float[][] m) {
		
		
		if (INFO) {
			System.out.println("Converting to Upper Triangle...");
		}

		float f1 = 0;
		float temp = 0;
		int tms = m.length; // get This Matrix Size (could be smaller than
							// global)
		int v = 1;

		iDF = 1;

		for (int col = 0; col < tms - 1; col++) {
			for (int row = col + 1; row < tms; row++) {
				v = 1;

				outahere: while (m[col][col] == 0) // check if 0 in diagonal
				{ // if so switch until not
					if (col + v >= tms) // check if switched all rows
					{
						iDF = 0;
						break outahere;
					} else {
						for (int c = 0; c < tms; c++) {
							temp = m[col][c];
							m[col][c] = m[col + v][c]; // switch rows
							m[col + v][c] = temp;
						}
						v++; // count row switchs
						iDF = iDF * -1; // each switch changes determinant
										// factor
					}
				}

				if (m[col][col] != 0) {
					if (DEBUG) {
						System.out.println("tms = " + tms + "   col = " + col
								+ "   row = " + row);
					}

					try {
						f1 = (-1) * m[row][col] / m[col][col];
						for (int i = col; i < tms; i++) {
							m[row][i] = f1 * m[col][i] + m[row][i];
						}
					} catch (Exception e) {
						System.out.println("Still Here!!!");
					}

				}

			}
		}

		return m;
	}

	// --------------------------------------------------------------

	public float Determinant() {
		float[][] matrix = this.matrix;
		
		if (INFO) {
			System.out.println("Getting Determinant...");
		}
		int tms = matrix.length;

		float det = 1;

		matrix = UpperTriangle(matrix);

		for (int i = 0; i < tms; i++) {
			det = det * matrix[i][i];
		} // multiply down diagonal

		det = det * iDF; // adjust w/ determinant factor

		if (INFO) {
			System.out.println("Determinant: " + det);
		}
		return det;
	}

	private float Determinant(float[][] matrix) {
		 
		
		if (INFO) {
			System.out.println("Getting Determinant...");
		}
		int tms = matrix.length;

		float det = 1;

		matrix = UpperTriangle(matrix);

		for (int i = 0; i < tms; i++) {
			det = det * matrix[i][i];
		} // multiply down diagonal

		det = det * iDF; // adjust w/ determinant factor

		if (INFO) {
			System.out.println("Determinant: " + det);
		}
		return det;
	}
	
	public Matrix addMatrix(Matrix m) throws Exception{
		if((m.matrix.length == this.matrix.length) && (m.matrix[0].length == this.matrix[0].length)){
				Matrix retval = new Matrix(this.matrix.length);
			for(int i = 0; i<this.matrix[0].length;i++){
					for(int j = 0; j<this.matrix.length;j++){
						retval.matrix[i][j] = this.matrix[i][j] + m.matrix[i][j];
					}
				}
			return retval;
		} else {
			throw new Exception();
		}
		
	}
	
	public Matrix subtractMatrix(Matrix m) throws Exception{
		if((m.matrix.length == this.matrix.length) && (m.matrix[0].length == this.matrix[0].length)){
				Matrix retval = new Matrix(this.matrix.length);
			for(int i = 0; i<this.matrix[0].length;i++){
					for(int j = 0; j<this.matrix.length;j++){
						retval.matrix[i][j] = this.matrix[i][j] - m.matrix[i][j];
					}
				}
			return retval;
		} else {
			throw new Exception();
		}
		
	}
	
	public Matrix divide(Matrix j){
		try {
			Matrix mi = this.Inverse();
			mi = mi.MultiplyMatrix(j);
			return mi;
		} catch (Exception e) {
			throw new RuntimeException("Invalid Matrix operation.");
		}
	}
	
    public boolean eq(Matrix B) {
        Matrix A = this;
        if (B.getMatrix().length != getMatrix().length || B.getMatrix()[0].length != getMatrix()[0].length) throw new RuntimeException("Illegal matrix dimensions.");
        for (int i = 0; i < this.getMatrix().length; i++)
            for (int j = 0; j < this.getMatrix()[0].length; j++)
                if (A.getMatrix()[i][j] != B.getMatrix()[i][j]) return false;
        return true;
    }

    public class RCProduct extends Thread {

    	private float[][] A;
    	private int row;
    	private float[][] B;
    	private int col;
    	private Matrix res;
    	private Semaphore s;
    	private int width;
    	private int height;

    	/**
    	 * @param a
    	 * @param row
    	 * @param b
    	 * @param col
    	 * @param res
    	 */
    	public RCProduct(float[][] a, int row, float[][] b, int col, Matrix res,Semaphore s,int width, int height) {
    		super();
    		this.A = a;
    		this.row = row;
    		this.B = b;
    		this.col = col;
    		this.res = res;
    		this.s = s;
    		this.width = width;
    		this.height = height;
    		try {
    			this.s.acquire();
    		} catch (InterruptedException e) {
    			// TODO Auto-generated catch block
    			e.printStackTrace();
    		}
    	}

    	public void run() {
    		for(int i = this.row; i< this.row + this.width; i++ ){
    			for(int j = this.col ; j< this.col + this.height; j++){
    				this.res.matrix[i][j] = this.calculateRowColumnProduct(A, i, B, j);

    			}
    		}
    				this.s.release();
    	}

    	public float calculateRowColumnProduct(float[][] A, int row, float[][] B,
    			int col) {
    		float product = 0;
    		for (int i = 0; i < A[row].length; i++)
    			product += A[row][i] * B[i][col];
    		return product;
    	}
    }
}