package Utils;

import com.mongodb.MongoClient;
import com.mongodb.MongoException;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import org.bson.Document;


/**
 * Created by ITTC-Jayvee on 2015/4/8.
 */
public class MongoDBUtils {
    private MongoDatabase db;

    public MongoDBUtils(String address, int port, String dbName) throws MongoNotSuchDBException {
        MongoClient mongoClient = new MongoClient(address, port);
        this.db = mongoClient.getDatabase(dbName);
        if (db.listCollectionNames().first() == null) {
            throw new MongoNotSuchDBException("Can not find database named " + dbName + "!");
        }
    }

    public MongoCollection<Document> getCollection(String collectionName) {

        MongoCollection<Document> collection = this.db.getCollection(collectionName);
        if (collection.count() != 0) {
            return collection;
        } else {
            throw new MongoNotSuchDBException("can not find collection named " + collectionName + "!");
        }
    }

    private class MongoNotSuchDBException extends MongoException {
        public MongoNotSuchDBException(String msg) {
            super(msg);
        }
    }

//    public void isConnected() {
//
//        System.out.println(db.getName());
//    }

    public MongoDatabase getDB() {
        return this.db;
    }


    public static void main(String a[]) {
        MongoDBUtils mongoDBUtils;
//        try {
        mongoDBUtils = new MongoDBUtils("10.108.192.165", 27017, "AppChinaData");
//        MongoDatabase mongoDatabase = mongoDBUtils.getDB();
        System.out.println(mongoDBUtils.getCollection("AppInfo"));
//        MongoCollection<Document> appInfo = mongoDatabase.getCollection("AppInfo");
//        appInfo.find(new BasicDBObject(""));
//        MongoIterable<String> strings = mongoDatabase.listCollectionNames();
//            System.out.println(strings.first());
//            for (String s : strings) {
//                System.out.println(s);
//            }

//        } catch (MongoNotSuchDBException e) {
//            e.printStackTrace();
//        }
//        mongoDBUtils.isConnected();
    }
}
