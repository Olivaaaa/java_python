package com.example.controller;

import com.alibaba.fastjson.JSONArray;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;

import java.io.*;
import java.util.*;

@Controller
public class ExecuteScript {

    @RequestMapping("/execpython")
    public Object execPython() throws IOException, InterruptedException {

        Runtime run = Runtime.getRuntime();
        Process process = run.exec("cmd /c start /wait G:\\java-python\\src\\main\\resources\\static\\run.bat");
        process.waitFor();
        System.out.println("finishing");


        return "执行python脚本成功";
    }

    @RequestMapping(value = "/executescript")
    public String reader(Model model) throws FileNotFoundException {
        try{
            BufferedReader reader = new BufferedReader(new FileReader("G:\\java-python\\src\\main\\resources\\static\\file\\OR.csv"));
//            reader.readLine();
            String line = null;
            List<Map<String, String>> resultList = new ArrayList<>();
//            Map<String, String> result = new HashMap<String, String>();
            while ((line = reader.readLine()) != null){
                Map<String, String> result = new HashMap<String, String>();
                String item[] = line.split(",");
                String name = item[0];
                System.out.println(name);
                result.put("name", name);
                String min = item[1];
                result.put("min", min);
                String max = item[2];
                result.put("max", max);
                String OR = item[item.length-1];
                result.put("OR", OR);
                resultList.add(result);
            }
            model.addAttribute("resultList", resultList);
            System.out.println(resultList);

    } catch (IOException e) {
            e.printStackTrace();
        }
        return "dashboard";
    }

    @RequestMapping("/user")
    public String user(){
        return "test";
    }
}

