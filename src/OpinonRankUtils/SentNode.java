package OpinonRankUtils;

public  class SentNode implements Comparable {
    String sent;
    double trustNess;

    public SentNode(String sent, double trustNess) {
        this.sent = sent;
        this.trustNess = trustNess;
    }

    public double getTrustNess() {
        return trustNess;
    }

    @Override
    public int compareTo(Object o) {
        o = (SentNode) o;
        if (this.getTrustNess() < ((SentNode) o).getTrustNess()) {
            return 1;
        } else if (this.getTrustNess() > ((SentNode) o).getTrustNess()) {
            return -1;
        } else {
            return 0;
        }
    }
}
