using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.IO;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Swat_Daycent_Pro
{
    public partial class Form1 : NForm
    {
        private Process progressTest;
        //private CancellationTokenSource _cts;      

        Form1 loginform = null;
        public Form1(Form1 myform)
        {
            this.loginform = myform;
            InitializeComponent();
        }

        private void Form1_FormClosed(object sender, FormClosedEventArgs e)
        {
           loginform.Close();
        }
        public Form1()
        {
            InitializeComponent();
            GetAllInitInfo(this.Controls[0]);
            Control.CheckForIllegalCrossThreadCalls = false; //加载时 取消跨线程检查

            //this.groupBox1.Paint += groupBox_Paint;
            //this.groupBox2.Paint += groupBox_Paint;
            //this.groupBox3.Paint += groupBox_Paint;
            //this.groupBox4.Paint += groupBox_Paint;
            //this.groupBox6.Paint += groupBox_Paint;
            //this.MouseWheel += new System.Windows.Forms.MouseEventHandler(this.pMouseWheel);
            //this.pictureBox1.MouseWheel += new System.Windows.Forms.MouseEventHandler(this.pictureBox1_MouseWheel);
        }

        public string main_path = "";
        public string main_path2 = "";//界面2的exe路径
        public string pathname = "";



        void groupBox_Paint(object sender, PaintEventArgs e)//画groupbox边框
        {
            GroupBox gBox = (GroupBox)sender;

            e.Graphics.Clear(gBox.BackColor);
            e.Graphics.DrawString(gBox.Text, gBox.Font, Brushes.Black, 10, 1);
            var vSize = e.Graphics.MeasureString(gBox.Text, gBox.Font);
            e.Graphics.DrawLine(Pens.Black, 1, vSize.Height / 2, 8, vSize.Height / 2);
            e.Graphics.DrawLine(Pens.Black, vSize.Width + 8, vSize.Height / 2, gBox.Width - 2, vSize.Height / 2);
            e.Graphics.DrawLine(Pens.Black, 1, vSize.Height / 2, 1, gBox.Height - 2);
            e.Graphics.DrawLine(Pens.Black, 1, gBox.Height - 2, gBox.Width - 2, gBox.Height - 2);
            e.Graphics.DrawLine(Pens.Black, gBox.Width - 2, vSize.Height / 2, gBox.Width - 2, gBox.Height - 2);
        }
        //Threadmain(task_id, Inpath, byear, eyear, Outpath, flag, ts, he);
        public void Threadmain(string task_id, string Inpath, string byear, string eyear, string Outpath, int flag, string ts, string he)
        {
            string cmdpath = main_path;
            string arg = "" + task_id + "" + " " + "" + Inpath + "" + " " + "" + byear + "" + " " + "" + eyear + "" + " " + "" + Outpath + "" + " " + "" + flag + "" + " " + "" + ts + "" + " " + "" + he + "";
            
            richTextBox1.Text = arg;
            //richTextBox1.Text = Inpath + System.Environment.NewLine + byear + System.Environment.NewLine + eyear + System.Environment.NewLine + Outpath + System.Environment.NewLine + ts + System.Environment.NewLine + he + System.Environment.NewLine + space + System.Environment.NewLine + se + System.Environment.NewLine + flag;
            Console.WriteLine(CallCMD(cmdpath, arg));
            
            richTextBox1.Text = CallCMD(cmdpath, arg);
            richTextBox1.Text = richTextBox1.Text + System.Environment.NewLine + "Completed!";
            MessageBox.Show("Task Cpmpleted!", "Finished", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
        }


        private void SleepT()
        {
            //for (int i = 0; i < 500; i++)
            //{
            //    System.Threading.Thread.Sleep(10);              
            //}
            String ss;
            String ts;
            string Inpath;
            string byear;
            string eyear;
            string Outpath;
            string ex;
            int flag = 1;
            String he = null;
            string task_id = "";
            int space = 1;
            int se = 1;
            int tss = 1;

            if (radioButton10.Checked)
            {
                ss = "Basin";
                space = 1;
            }
            else if (radioButton11.Checked)
            {
                ss = "Subbasin";
                space = 2;
            }
            else if (radioButton12.Checked)
            {
                ss = "Hru";
                space = 3;
            }
            else if (radioButton13.Checked)
            {
                ss = "Lulc";
                space = 4;
            }
            else if (radioButton1.Checked)
            {
                ss = "Rch";
                space = 5;
            }
            else
            {
                ss = " ";
            }

            

            if (checkBox2.Checked&&!checkBox3.Checked&&!checkBox4.Checked)
            {
                ts = "year";
            }
            else if (checkBox3.Checked&&!checkBox2.Checked&&!checkBox4.Checked)
            {
                ts = "season";
            }
            else if (checkBox4.Checked&&!checkBox2.Checked&&!checkBox3.Checked)
            {
                ts = "month";
            }
            else if (!checkBox4.Checked && checkBox2.Checked && checkBox3.Checked)
            {
                ts = "year,season";
            }
            else if (checkBox4.Checked && checkBox2.Checked && !checkBox3.Checked)
            {
                ts = "year,month";
            }
            else if (checkBox4.Checked && !checkBox2.Checked && checkBox3.Checked)
            {
                ts = "season,month";
            }
            else if (checkBox4.Checked && checkBox2.Checked && checkBox3.Checked)
            {
                ts = "year,season,month";
            }
            else
            {
                ts = "none";
            }


            if (textBox5.Text.Contains("\\"))
            {
                textBox5.Text = textBox5.Text.Replace("\\", "/");
            }
            textBox3.Text = textBox5.Text + "/output_result/";
            //textBox4.Text = textBox5.Text + "/output_result/";
            Inpath = textBox5.Text;
            byear = textBox1.Text;
            eyear = textBox2.Text;
            Outpath = textBox3.Text;

            if (checkBox1.Checked)
            {
                flag = 1;
            }
            else
            {
                flag = 0;
            }

            

            if (radioButton18.Checked && radioButton10.Checked)
            {
                task_id = "1";
                he = textBox7.Text;
            }
            else if (radioButton18.Checked && radioButton13.Checked)
            {
                task_id = "2";
                he = textBox7.Text;
            }
            else if (radioButton18.Checked && radioButton12.Checked)
            {
                task_id = "3";
                he = textBox7.Text;
            }
            else if (radioButton18.Checked && radioButton1.Checked)
            {
                task_id = "4";
                he = textBox7.Text;
            }
            else if (radioButton18.Checked && radioButton11.Checked)
            {
                task_id = "5";
                he = textBox7.Text;
            }
            else if (radioButton19.Checked && radioButton10.Checked)
            {
                task_id = "6";
                he = textBox6.Text;
            }
            else if (radioButton19.Checked && radioButton12.Checked)
            {
                task_id = "7";
                he = textBox6.Text;
            }
            else if (radioButton19.Checked && radioButton11.Checked)
            {
                task_id = "8";
                he = textBox6.Text;
            }
            else if (radioButton19.Checked && radioButton13.Checked)
            {
                task_id = "9";
                he = textBox6.Text;
            }

            if (Inpath.Contains("\\"))
            {
                Inpath = Inpath.Replace("\\", "/");
            }
            if (Outpath.Contains("\\"))
            {
                Outpath = Outpath.Replace("\\", "/");
            }
            //Threadmain(Inpath, byear, eyear, Outpath, flag, ts, he, space, se);
            Threadmain(task_id, Inpath, byear, eyear, Outpath, flag, ts, he);
        }
        public static string CallCMD(string _command, string _arguments)
        {
            System.Diagnostics.ProcessStartInfo psi = new System.Diagnostics.ProcessStartInfo(_command, _arguments);
            psi.CreateNoWindow = true;
            psi.RedirectStandardOutput = true;
            psi.UseShellExecute = false;
            System.Diagnostics.Process p = System.Diagnostics.Process.Start(psi);
            return (p.StandardOutput.ReadToEnd());
        }

        //private void button2_Click(object sender, EventArgs e)
        //{
        //    Form2 form2 = new Form2();
        //    form2.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
        //    form2.ShowDialog();
        //}


        //private void button5_Click(object sender, EventArgs e)
        //{
            //string Path = "";
            //FolderBrowserDialog folder = new FolderBrowserDialog();
            //folder.Description = "选择main.exe所在文件夹目录";  //提示的文字
            //if (folder.ShowDialog() == DialogResult.OK)
            //{
            //    main_path = folder.SelectedPath;
            //}
            //OpenFileDialog dlg = new OpenFileDialog();
            //dlg.Filter = "应用程序(*.exe)|*.exe";//文件的类型及说明
            //if (dlg.ShowDialog() == DialogResult.OK)//选中确定后
            //{
            //    string filePath = dlg.FileName;
            //    main_path = filePath;
            //}
        //}


        private void radioButton1_checked(object sender, EventArgs e)
        {
            if (radioButton1.Checked == true)
            {
                checkBox2.Enabled = false;
                checkBox3.Enabled = false;
                checkBox4.Enabled = false;
                textBox7.Text = "FLOW_OUT/cms,SED_OUT/tons";
                checkBox2.Checked = false;
                checkBox3.Checked = false;
                checkBox4.Checked = false;

            }
            else
            {
                checkBox2.Enabled = true;
                checkBox3.Enabled = true;
                checkBox4.Enabled = true;
            }
        }

        private void radioButton13_checked(object sender, EventArgs e)
        {
            if (radioButton13.Checked == true)
            {
                checkBox2.Enabled = false;
                checkBox3.Enabled = false;
                checkBox4.Enabled = false;
                textBox7.Text = "PCP/mm,ET/mm,SW_END/mm";
                checkBox2.Checked = false;
                checkBox3.Checked = false;
                checkBox4.Checked = false;
            }
            else
            {
                checkBox2.Enabled = true;
                checkBox3.Enabled = true;
                checkBox4.Enabled = true;
            }
        }

        private void radioButton12_checked(object sender, EventArgs e)
        {
            if (radioButton12.Checked == true)
            {
                checkBox2.Enabled = false;
                checkBox3.Enabled = false;
                checkBox4.Enabled = false;
                textBox7.Text = "PCP/mm,ET/mm,SW_END/mm";
                checkBox2.Checked = false;
                checkBox3.Checked = false;
                checkBox4.Checked = false;
            }
            else
            {
                checkBox2.Enabled = true;
                checkBox3.Enabled = true;
                checkBox4.Enabled = true;
            }
        }

        private void radioButton11_checked(object sender, EventArgs e)
        {
            if (radioButton11.Checked == true)
            {
                checkBox2.Enabled = false;
                checkBox3.Enabled = false;
                checkBox4.Enabled = false;
                textBox7.Text = "SYLD/t/ha,ORGN/kg/ha";
                checkBox2.Checked = false;
                checkBox3.Checked = false;
                checkBox4.Checked = false;
            }
            else
            {
                checkBox2.Enabled = true;
                checkBox3.Enabled = true;
                checkBox4.Enabled = true;
            }
        }

        private void radioButton10_checked(object sender, EventArgs e)
        {
            if (radioButton10.Checked == true)
            {
                checkBox2.Enabled = true;
                checkBox3.Enabled = true;
                checkBox4.Enabled = true;
                textBox7.Text = "PCP/mm,ET/mm,SW_END/mm";
            }
            
        }

        private void linkLabel1_LinkClicked(object sender, LinkLabelLinkClickedEventArgs e)
        {
            string Path = "";
            FolderBrowserDialog folder = new FolderBrowserDialog();
            folder.Description = "选择文件所在文件夹目录";  //提示的文字
            if (folder.ShowDialog() == DialogResult.OK)
            {
                Path = folder.SelectedPath;
            }
            textBox5.Text = Path;
        }

        private void button4_Click(object sender, EventArgs e)
        {
            Form3 form3 = new Form3();
            form3.Owner = this;
            form3.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
            form3.ShowDialog();
            textBox6.Text = strValue;
        }

        private void button3_Click(object sender, EventArgs e)
        {
            /*string fileStream;
            //MessageBox.Show("目前还没有海报信息！！！");
            pictureBox1.SizeMode = PictureBoxSizeMode.Zoom;
            fileStream = new FileStream("图片路径", FileMode.Open, FileAccess.Read);
            pictureBox1.Image = Image.FromStream(fileStream);*/
            string outpath = "";
            string sc = "";
            string tc = "";
            string ele = "";
            outpath = textBox3.Text;
            if (outpath.Contains("\\"))
            {
                outpath = outpath.Replace("\\", "/");
            }
            /*
            if (radioButton10.Checked)
            {
                sc = "Basin";
            }
            else if (radioButton11.Checked)
            {
                sc = "Subbasin";
            }
            else if (radioButton12.Checked)
            {
                sc = "Hru";
            }
            else if (radioButton13.Checked)
            {
                sc = "Lulc";
            }
            else if (radioButton1.Checked)
            {
                sc = "Rch";
            }
            */
            
            /*
            if (checkBox2.Checked && !checkBox3.Checked && !checkBox4.Checked)
            {
                tc = "year";
            }
            else if (checkBox3.Checked && !checkBox2.Checked && !checkBox4.Checked)
            {
                tc = "season";
            }
            else if (checkBox4.Checked && !checkBox2.Checked && !checkBox3.Checked)
            {
                tc = "month";
            }
            else if (!checkBox4.Checked && checkBox2.Checked && checkBox3.Checked)
            {
                tc = "year,season";
            }
            else if (checkBox4.Checked && checkBox2.Checked && !checkBox3.Checked)
            {
                tc = "year,month";
            }
            else if (checkBox4.Checked && !checkBox2.Checked && checkBox3.Checked)
            {
                tc = "season,month";
            }
            else if (checkBox4.Checked && checkBox2.Checked && checkBox3.Checked)
            {
                tc = "year,season,month";
            }
            else
            {
                tc = " ";
            }
            //else if (radioButton17.Checked)
            //{
            //    tc = "day";
            //}

            if (radioButton18.Checked)
            {
                ele = "HydroParameter";
            }
            else if (radioButton19.Checked)
            {
                ele = "EcoParameter";
            }
            */

            if(radioButton10.Checked && radioButton18.Checked)
            {
                pathname = "" + outpath + "" + "\\" + "" + "HydroParameter_Basin_Year.tif";
            }
            else if(radioButton13.Checked && radioButton18.Checked)
            {
                pathname = "" + outpath + "" + "\\" + "" + "HydroPars_lulc_ny_mean.tif";
            }
            else if (radioButton12.Checked && radioButton18.Checked)
            {
                pathname = "" + outpath + "" + "\\" + "" + "HydroParameter_Hru_distribution.tif";
            }
            else if (radioButton1.Checked && radioButton18.Checked)
            {
                pathname = "" + outpath + "" + "\\" + "" + "HydroParameter_rch_distribution.tif";
            }
            else if (radioButton11.Checked && radioButton18.Checked)
            {
                pathname = "" + outpath + "" + "\\" + "" + "HydroParameter_Sub_distribution.tif";
            }
            else if (radioButton10.Checked && radioButton19.Checked)
            {
                pathname = "" + outpath + "" + "\\" + "" + "EcoParameter_Basin_Year.tif";
            }
            else if (radioButton12.Checked && radioButton19.Checked)
            {
                pathname = "" + outpath + "" + "\\" + "" + "EcoParameter_Hru_distribution.tif";
            }
            else if (radioButton11.Checked && radioButton19.Checked)
            {
                pathname = "" + outpath + "" + "\\" + "" + "EcoParameter_Sub_distribution.tif";
            }
            else if (radioButton13.Checked && radioButton19.Checked)
            {
                pathname = "" + outpath + "" + "\\" + "" + "EcoPars_lulc_ny_mean.tif";
            }


            //pathname = "" + outpath + "" + "\\" + "" + ele + "" + "_" + "" + sc + "" + "_" + "" + tc + "" + ".tif";
            //richTextBox1.Text = pathname;
            if (outpath != "")
            {
                this.pictureBox1.Load(pathname);
            }
            else
            {
                MessageBox.Show("请先运行！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            String ss;
            String ts;
            string Inpath;
            string byear;
            string eyear;
            string Outpath;
            string ex;
            int flag = 1;
            String he = null;
            int space = 1;
            int se = 1;
            int tss = 1;

            if (radioButton10.Checked)
            {
                ss = "Basin";
                space = 1;
            }
            else if (radioButton11.Checked)
            {
                ss = "Subbasin";
                space = 2;
            }
            else if (radioButton12.Checked)
            {
                ss = "Hru";
                space = 3;
            }
            else if (radioButton13.Checked)
            {
                ss = "Lulc";
                space = 4;
            }
            else if (radioButton1.Checked)
            {
                ss = "Rch";
                space = 5;
            }
            else
            {
                ss = " ";
            }

            

            if (checkBox2.Checked && !checkBox3.Checked && !checkBox4.Checked)
            {
                ts = "year";
            }
            else if (checkBox3.Checked && !checkBox2.Checked && !checkBox4.Checked)
            {
                ts = "season";
            }
            else if (checkBox4.Checked && !checkBox2.Checked && !checkBox3.Checked)
            {
                ts = "month";
            }
            else if (!checkBox4.Checked && checkBox2.Checked && checkBox3.Checked)
            {
                ts = "year,season";
            }
            else if (checkBox4.Checked && checkBox2.Checked && !checkBox3.Checked)
            {
                ts = "year,month";
            }
            else if (checkBox4.Checked && !checkBox2.Checked && checkBox3.Checked)
            {
                ts = "season,month";
            }
            else if (checkBox4.Checked && checkBox2.Checked && checkBox3.Checked)
            {
                ts = "year,season,month";
            }
            else
            {
                ts = " ";
            }

            // richTextBox2.Text = textBox5.Text + " " + textBox1.Text + " " + textBox2.Text + " " + ss + " " + 
            //     ts + " " + comboBox1.Text + " " + comboBox2.Text;

            if (textBox5.Text.Contains("\\"))
            {
                textBox5.Text = textBox5.Text.Replace("\\", "/");
            }
            textBox3.Text = textBox5.Text + "/output_result/";
            //textBox4.Text = textBox5.Text + "/output_result/";
            Inpath = textBox5.Text;
            byear = textBox1.Text;
            eyear = textBox2.Text;
            Outpath = textBox3.Text;

            if (checkBox1.Checked)
            {
                flag = 1;
            }
            else 
            {
                flag = 0;
            }

            if (radioButton18.Checked)
            {
                he = textBox7.Text;
                se = 1;
                ex = "HydroParameter";
            }
            else if (radioButton19.Checked)
            {
                he = textBox6.Text;
                se = 2;
                ex = "EcoParameter";
            }
            else
            {
                //MessageBox.Show("请选择元素！");
            }

            if (Inpath.Contains("\\"))
            {
                Inpath = Inpath.Replace("\\", "/");
            }
            if (Outpath.Contains("\\"))
            {
                Outpath = Outpath.Replace("\\", "/");
            }

            //Thread fThread = new Thread(new ThreadStart(SleepT));
            //fThread.Start();

            //暂时
            
            if (Inpath == "")
            {
                MessageBox.Show("请选择输入路径！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else if (radioButton1.Checked && radioButton19.Checked)
            {
                MessageBox.Show("Ecological elements不能选择Rch！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else if (byear == "")
            {
                MessageBox.Show("请输入开始年份！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else if (eyear == "")
            {
                MessageBox.Show("请输入结束年份！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else
            {
                OpenFileDialog dlg = new OpenFileDialog();
                dlg.Filter = "应用程序(*.exe)|*.exe";//文件的类型及说明
                if (dlg.ShowDialog() == DialogResult.OK)//选中确定后
                {
                    string filePath = dlg.FileName;
                    main_path = filePath;
                }
                if (main_path != "")
                {
                    Thread fThread = new Thread(new ThreadStart(SleepT));
                    fThread.Start();
                }
                else
                {
                    MessageBox.Show("请选择main.exe路径！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }

                //Threadmain(Inpath, byear, eyear, Outpath, flag, ts, he, space, se);
                //string cmdpath = main_path;
                //string arg = "" + Inpath + "" + " " + "" + byear + "" + " " + "" + eyear + "" + " " + "" + Outpath + "" + " " + "" + flag + "" + " " + "" + ts + "" + " " + "" + he + "" + " " + "" + space + "" + " " + "" + se + "";
                //_cts = new CancellationTokenSource();
                //ThreadPool.QueueUserWorkItem(state => Console.WriteLine(CallCMD(cmdpath, arg)));
                //Console.WriteLine(CallCMD(cmdpath, arg));
                //richTextBox1.Text = CallCMD(cmdpath, arg);
            }

            //string cmdpath = "C://Users/hp/Desktop/Test/main.exe"; 核心语句
            //string cmdpath = "C://Users/hp/Desktop/Swat_Day/dist/main.exe";
            //string cmdpath = main_path;
            //string arguments = "1 2 3 4 5 6 7";
            //string arg = "" + Inpath + "" + " " + "" + byear + "" + " " + "" + eyear + "" + " " + "" + Outpath + "" + " " + "" + flag + "" + " " + "" + ts + "" + " " + "" + he + "" + " " + "" + space + "" + " " + "" + se + "";
            //Console.WriteLine(CallCMD(cmdpath, arg));
            //richTextBox1.Text = CallCMD(cmdpath, arg);
            //richTextBox1.Text = arg;
        }

        private void button2_Click(object sender, EventArgs e)
        {
            if (radioButton10.Checked||radioButton12.Checked||radioButton13.Checked)
            {
                //Form2 form2 = new Form2();
                //form2.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
                //form2.ShowDialog();


                Form2 frm2 = new Form2();
                //frm21.Text = "G:/SWAT-DayCent_software_test/Water_Retention/WR1";
                //frm21.Show();
                frm2.Owner = this;
                frm2.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
                frm2.ShowDialog();
            }
            else if (radioButton11.Checked)
            {
                Form5 form5 = new Form5();
                form5.Owner = this;
                form5.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
                form5.ShowDialog();
            }
            else if (radioButton1.Checked)
            {
                Form6 form6 = new Form6();
                form6.Owner = this;
                form6.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
                form6.ShowDialog();
            }
            textBox7.Text = strValue;
        }

        private void linkLabel2_LinkClicked(object sender, LinkLabelLinkClickedEventArgs e)
        {
            string outpath;
            //outpath = @"C:\Users\hp\Desktop\SWAT_DayCent_Pro\output_result";
            outpath = @textBox3.Text;
            if (outpath.Contains("/"))
            {
                outpath = outpath.Replace("/", "\\");
            }
            System.Diagnostics.Process.Start("explorer.exe", outpath);
        }

        private void linkLabel3_LinkClicked(object sender, LinkLabelLinkClickedEventArgs e)
        {
            string outpath;
            //outpath = @"C:\Users\hp\Desktop\SWAT_DayCent_Pro\output_result";
            outpath = @textBox3.Text;
            if (outpath.Contains("/"))
            {
                outpath = outpath.Replace("/", "\\");
            }
            System.Diagnostics.Process.Start("explorer.exe", outpath);
        }




        //界面二

        int id;
        string pathname2 = "";
        public int Getid()
        {
            if (radioButton2.Checked)
            {
                id = 1;
            }
            else if (radioButton3.Checked)
            {
                id = 2;
            }
            else if (radioButton4.Checked)
            {
                id = 3;
            }
            else if (radioButton5.Checked)
            {
                id = 4;
            }
            else if (radioButton6.Checked)
            {
                id = 5;
            }
            else if (radioButton7.Checked)
            {
                id = 6;
            }
            return id;
        }
        private string strValue;
        public string StrValue
        {
            set
            {
                strValue = value;
            }
        }

        private string stroutdir;
        //string dir;
        public string Stroutdir
        {
            set
            {
                stroutdir = value;
            }
        }

        //private void btnShowForm2_Click(object sender, EventArgs e)
        //{
        //    Form2 lForm = new Form2();
        //    lForm.Owner = this;//重要的一步，主要是使Form2的Owner指针指向Form1
        //    lForm.ShowDialog();
        //    MessageBox.Show(strValue);//显示返回的值
        //}


        private void button6_Click(object sender, EventArgs e)
        {

            if (radioButton2.Checked||radioButton4.Checked||radioButton6.Checked)//子窗体给父窗体传值
            {
                if (radioButton2.Checked)
                {
                    Form21 frm21 = new Form21("C:/Users/21414/Desktop/software1/main12/SWAT-DayCent_software_test/Water_Retention/WR1");
                    //frm21.Text = "G:/SWAT-DayCent_software_test/Water_Retention/WR1";
                    //frm21.Show();
                    frm21.Owner = this;
                    frm21.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
                    frm21.ShowDialog();
                }
                else if (radioButton4.Checked)
                {
                    Form21 frm21 = new Form21("C:/Users/21414/Desktop/software1/main12/SWAT-DayCent_software_test/Soil_Erosion/Soil_Ero_M1");
                    //frm21.Text = "G:/SWAT-DayCent_software_test/Soil_Erosion/Soil_Ero_M1";
                    //frm21.Show();
                    frm21.Owner = this;
                    frm21.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
                    frm21.ShowDialog();
                }
                else if (radioButton6.Checked)
                {
                    Form21 frm21 = new Form21("C:/Users/21414/Desktop/software1/main12/SWAT-DayCent_software_test/Carbon_cal/Carbon_M1");
                    //frm21.Text = "G:/SWAT-DayCent_software_test/Carbon_cal/Carbon_M1";
                    //frm21.Show();
                    frm21.Owner = this;
                    frm21.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
                    frm21.ShowDialog();
                }
                //Form21 form21 = new Form21();
                //form21.Owner = this;
                //form21.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
                //form21.ShowDialog();
                richTextBox3.Text = strValue;
            }
            else if (radioButton3.Checked)
            {
                Form22 form22 = new Form22();
                form22.Owner = this;
                form22.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
                form22.ShowDialog();
                richTextBox3.Text = strValue;
            }
            else if (radioButton5.Checked||radioButton7.Checked)
            {
                if (radioButton5.Checked)
                {
                    Form23 frm23 = new Form23("C:/Users/21414/Desktop/software1/main12/SWAT-DayCent_software_test/Soil_Erosion/Soil_Ero_M2");
                    //frm21.Text = "G:/SWAT-DayCent_software_test/Water_Retention/WR1";
                    //frm21.Show();
                    frm23.Owner = this;
                    frm23.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
                    frm23.ShowDialog();
                }
                else if (radioButton7.Checked)
                {
                    Form23 frm23 = new Form23("C:/Users/21414/Desktop/software1/main12/SWAT-DayCent_software_test/Carbon_cal/Carbon_M2");
                    //frm21.Text = "G:/SWAT-DayCent_software_test/Soil_Erosion/Soil_Ero_M1";
                    //frm21.Show();
                    frm23.Owner = this;
                    frm23.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
                    frm23.ShowDialog();
                }
                //Form23 form23 = new Form23();
                //form23.Owner = this;
                //form23.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
                //form23.ShowDialog();
                richTextBox3.Text = strValue;
            }
            
        }

        //private void button8_Click(object sender, EventArgs e)
        //{
        //    OpenFileDialog dlg = new OpenFileDialog();
        //    dlg.Filter = "应用程序(*.exe)|*.exe";//文件的类型及说明
        //    if (dlg.ShowDialog() == DialogResult.OK)//选中确定后
        //    {
        //        string filePath = dlg.FileName;
        //        main_path2 = filePath;
        //    }
        //}

        private void button7_Click(object sender, EventArgs e)
        {
            
            if (richTextBox3.Text == "")
            {
                MessageBox.Show("请选择参数！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else
            {
                OpenFileDialog dlg = new OpenFileDialog();
                dlg.Filter = "应用程序(*.exe)|*.exe";//文件的类型及说明
                if (dlg.ShowDialog() == DialogResult.OK)//选中确定后
                {
                    string filePath = dlg.FileName;
                    main_path2 = filePath;
                }
                if(main_path2 != "")
                {
                    Thread fThread = new Thread(new ThreadStart(SleepT2));
                    fThread.Start();
                }
                else
                {
                    MessageBox.Show("请选择main.exe路径！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
                
            }
            //Thread fThread = new Thread(new ThreadStart(SleepT2));
            //fThread.Start();
        }

        private void SleepT2()
        {
            string values = "";
            id = Getid();
            values = richTextBox3.Text;
            Threadmain2(values,id);
        }

        public void Threadmain2(string values,int id)
        {
            string cmdpath = main_path2;
            // string arg = "" + Inpath + "" + " " + "" + byear + "" + " " + "" + eyear + "" + " " + "" + Outpath + "" + " " + "" + flag + "" + " " + "" + ts + "" + " " + "" + he + "" + " " + "" + space + "" + " " + "" + se + "";
            string arg = "" + id + "" + " " + "" + values + "";

            richTextBox2.Text = arg;
            Console.WriteLine(CallCMD(cmdpath, arg));
            richTextBox2.Text = CallCMD(cmdpath, arg);
            richTextBox2.Text = richTextBox2.Text + System.Environment.NewLine + "Completed!";
            MessageBox.Show("Task Cpmpleted!", "Finished", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
        }

        private void button9_Click(object sender, EventArgs e)
        {
            if (radioButton2.Checked)
            {
                Form21 form21 = new Form21();
                form21.Owner = this;
                pathname2 = stroutdir;
                pathname2 += "\\";
                pathname2 += "WR1_Basin_Year.tif";
                //richTextBox2.Text = pathname2;
            }
            else if (radioButton3.Checked)
            {
                Form21 form21 = new Form21();
                form21.Owner = this;
                pathname2 = stroutdir;
                pathname2 += "\\";
                pathname2 += "WR2_Hru_distribution.tif";
                //richTextBox2.Text = pathname2;
            }
            else if (radioButton4.Checked)
            {
                Form21 form21 = new Form21();
                form21.Owner = this;
                pathname2 = stroutdir;
                pathname2 += "\\";
                pathname2 += "SYLD_Basin_Year.tif";
                //richTextBox2.Text = pathname2;
            }
            else if (radioButton5.Checked)
            {
                Form21 form21 = new Form21();
                form21.Owner = this;
                pathname2 = stroutdir;
                pathname2 += "\\";
                pathname2 += "SDR_space.tif";
                //richTextBox2.Text = pathname2;
            }
            else if (radioButton6.Checked)
            {
                Form21 form21 = new Form21();
                form21.Owner = this;
                pathname2 = stroutdir;
                pathname2 += "\\";
                pathname2 += "NPP_Basin_Year.tif";
                //richTextBox2.Text = pathname2;
            }
            else if (radioButton7.Checked)
            {
                Form21 form21 = new Form21();
                form21.Owner = this;
                pathname2 = stroutdir;
                pathname2 += "\\";
                pathname2 += "carbon_space.tif";
                //richTextBox2.Text = pathname2;
            }
            //pathname2 = ;
            //richTextBox1.Text = pathname;
            if (File.Exists(pathname2))
            {
                this.pictureBox2.Load(pathname2);
            }
            else
            {
                MessageBox.Show("未找到该文件！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            //else
            //{
            //    MessageBox.Show("请先运行！", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            //}
        }

        private void checkBox2_CheckedChanged(object sender, EventArgs e)
        {

        }
    }

    public partial class NForm : Form
    {
        #region 控件缩放
        double formWidth;//窗体原始宽度
        double formHeight;//窗体原始高度
        double scaleX;//水平缩放比例
        double scaleY;//垂直缩放比例
        Dictionary<string, string> controlInfo = new Dictionary<string, string>();
        //控件中心Left,Top,控件Width,控件Height,控件字体Size
        /// <summary>
        /// 获取所有原始数据
        /// </summary>
        protected void GetAllInitInfo(Control CrlContainer)
        {
            if (CrlContainer.Parent == this)
            {
                formWidth = Convert.ToDouble(CrlContainer.Width);
                formHeight = Convert.ToDouble(CrlContainer.Height);
            }
            foreach (Control item in CrlContainer.Controls)
            {
                if (item.Name.Trim() != "")
                    controlInfo.Add(item.Name, (item.Left + item.Width / 2) + "," + (item.Top + item.Height / 2) + "," + item.Width + "," + item.Height + "," + item.Font.Size);
                if ((item as UserControl) == null && item.Controls.Count > 0)
                    GetAllInitInfo(item);
            }
        }
        private void ControlsChangeInit(Control CrlContainer)
        {
            scaleX = (Convert.ToDouble(CrlContainer.Width) / formWidth);
            scaleY = (Convert.ToDouble(CrlContainer.Height) / formHeight);
        }
        private void ControlsChange(Control CrlContainer)
        {
            double[] pos = new double[5];//pos数组保存当前控件中心Left,Top,控件Width,控件Height,控件字体Size
            foreach (Control item in CrlContainer.Controls)
            {
                if (item.Name.Trim() != "")
                {
                    if ((item as UserControl) == null && item.Controls.Count > 0)
                        ControlsChange(item);
                    string[] strs = controlInfo[item.Name].Split(',');
                    for (int j = 0; j < 5; j++)
                    {
                        pos[j] = Convert.ToDouble(strs[j]);
                    }
                    double itemWidth = pos[2] * scaleX;
                    double itemHeight = pos[3] * scaleY;
                    item.Left = Convert.ToInt32(pos[0] * scaleX - itemWidth / 2);
                    item.Top = Convert.ToInt32(pos[1] * scaleY - itemHeight / 2);
                    item.Width = Convert.ToInt32(itemWidth);
                    item.Height = Convert.ToInt32(itemHeight);
                    try
                    {
                        item.Font = new Font(item.Font.Name, float.Parse((pos[4] * Math.Min(scaleX, scaleY)).ToString()));
                    }
                    catch
                    {
                    }
                }
            }
        }

        #endregion


        protected override void OnSizeChanged(EventArgs e)
        {
            base.OnSizeChanged(e);
            if (controlInfo.Count > 0)
            {
                ControlsChangeInit(this.Controls[0]);
                ControlsChange(this.Controls[0]);
            }
        }
    }
}
