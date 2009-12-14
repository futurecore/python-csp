package JyCSP.Interfaces;

public interface JyCspAltInterface {

	public void poison();
	public Object pri_select();
	public Object select();
	public Object fair_select();
	public Object last_selected();
	public boolean hasNext();
	public int getGuardLength();
		
}
