using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Swat_Daycent_Pro
{
    public partial class Form21 : Form
    {
        public Form21()
        {
            InitializeComponent();
        }
        int flag;

        //string tx11 = "";
        //string tx12 = "";
        //public string Text
        //{
            
            //string[] v = this.value.Split(",");
            //set {
                //string[] v = value.Split(',');
                //tx11 = v[0];
                //tx12 = v[1];
                //this.textBox1.Text = value;
                //this.textBox2.Text = v[1];
            //}
            //get { 
            //    return this.textBox1.Text; 
            //}

        //}
        public Form21(string strTextBox1Text)
        {
            InitializeComponent();
            this.textBox1.Text = strTextBox1Text;
            this.textBox4.Text = strTextBox1Text;
        }

        private void button1_Click(object sender, EventArgs e)
        {
            //textBox2.Text = textBox1.Text;
            if (checkBox1.Checked)
            {
                flag = 1;
             }
            else
            {
                flag = 0;
            }

            if (textBox1.Text.Contains("\\"))
            {
                textBox1.Text = textBox1.Text.Replace("\\", "/");
            }

            if (textBox2.Text.Contains("\\"))
            {
                textBox2.Text = textBox2.Text.Replace("\\", "/");
            }

            if (textBox3.Text.Contains("\\"))
            {
                textBox3.Text = textBox3.Text.Replace("\\", "/");
            }

            if (textBox4.Text.Contains("\\"))
            {
                textBox4.Text = textBox4.Text.Replace("\\", "/");
            }
            //Form1 lForm = new Form1();//实例化一个Form1窗口
            //lForm.String1 = textBox1.Text + " " + textBox2.Text + " " + textBox3.Text + " " + textBox4.Text + " " + flag;//设置Form1中string1的值
            //lForm.SetValue();//设置Form2中Label1的
            //lForm.ShowDialog();
            //lForm.Close();

            Form1 lForm1 = (Form1)this.Owner;//把Form2的父窗口指针赋给lForm1
            lForm1.Stroutdir = textBox4.Text;
            lForm1.StrValue = textBox1.Text + " " + textBox2.Text + " " + textBox3.Text + " " + textBox4.Text + " " + flag;//使用父窗口指针赋值
            this.Close();

        }
    }
}
