package com.example.controller;

import org.python.core.Py;
import org.python.core.PySystemState;
import org.python.util.PythonInterpreter;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

import java.io.*;

@Controller
@RequestMapping("/executescript")
public class ExecuteScript {

    @RequestMapping("/execpython")
    public Object execPython(){

        File file = new File("G:\\java-python\\src\\main\\resources\\static\\process_data.py");

        if(file.exists()){
            System.out.println("可以读取到非项目中脚本");
        }else{
            System.out.println("不可以读取到非项目中脚本");
            return "不可以读取到非项目中脚本";
        }


        PythonInterpreter interpreter = new PythonInterpreter();

        InputStream in = null;

        try {
            in = new FileInputStream("G:\\java-python\\src\\main\\resources\\static\\process_data.py");

            PySystemState sys = Py.getSystemState();

            sys.path.add("G:\\java-python\\src\\main\\resources\\static");

            interpreter.execfile(in);

        } catch (FileNotFoundException e) {
            e.printStackTrace();
            return "未找到文件";
        } catch (Exception e) {
            e.printStackTrace();

            if(null!=in){
                try {
                    in.close();
                } catch (IOException e1) {
                    // TODO Auto-generated catch block
                    e1.printStackTrace();
                }
            }
            return "执行python脚本失败";
        }

        return "执行python脚本成功";
    }

//    @RequestMapping("/execpython")
//    public Object execPython(){
//
//        File file = new File("G:\\java-python\\src\\main\\resources\\static\\test.py");
//
//        if(file.exists()){
//            System.out.println("可以读取到非项目中脚本");
//        }else{
//            System.out.println("不可以读取到非项目中脚本");
//            return "不可以读取到非项目中脚本";
//        }
//
//
//        PythonInterpreter interpreter = new PythonInterpreter();
//
//        InputStream in = null;
//
//        try {
//            in = new FileInputStream("G:\\java-python\\src\\main\\resources\\static\\test.py");
//
//            PySystemState sys = Py.getSystemState();
//
//            sys.path.add("G:\\java-python\\src\\main\\resources\\static");
//
//            interpreter.execfile(in);
//
//        } catch (FileNotFoundException e) {
//            e.printStackTrace();
//            return "未找到文件";
//        } catch (Exception e) {
//            e.printStackTrace();
//
//            if(null!=in){
//                try {
//                    in.close();
//                } catch (IOException e1) {
//                    // TODO Auto-generated catch block
//                    e1.printStackTrace();
//                }
//            }
//            return "执行python脚本失败";
//        }
//
//        return "执行python脚本成功";
//    }
}

