package JyCSP;

public interface JyCspAltInterface {

	public void poison();
	public Object preselect();
	public Object select();
	public Object fair_select();
	public Object last_selected();
	public boolean hasNext();
	public int getGuardLength();
		
}
